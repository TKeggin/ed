import requests as req
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import itertools
from tqdm import tqdm
from functools import lru_cache
from io import StringIO
import argparse
from numba import jit
import math

# Helper Functions
@jit(nopython=True)
def dist(a, b):
    """ Calculate cartesian distance between 2 points (a, b) in 3D """
    return np.sqrt((a[0] - b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

@lru_cache(maxsize=1)
def get_all_prices():
    """ Downloads all prices from EDDB. This is a huge file and takes a long time to download. """
    r = req.get("https://eddb.io/archive/v6/listings.csv", headers={'Accept-Encoding': 'gzip, deflate, sdch'})
    return pd.read_csv(StringIO(r.text))

@lru_cache(maxsize=1)
def get_systems():
    """ Download all the Populated Systems from EDDB. Returns a tuple of the systems, and their coordinates """
    r = req.get("https://eddb.io/archive/v6/systems_populated.json")
    systems = pd.DataFrame(r.json())
    system_coords = systems.set_index('name')[['x','y','z']].apply(lambda x : tuple(x), axis=1)
    return systems, system_coords

# Main Functions

def get_arb_ops():
    """ Find the most arbitragable commodites on EDDB """
    r = req.get("https://eddb.io/commodity")
    soup = BeautifulSoup(r.content, parser='lxml', features='lxml')
    table = soup.find('table', attrs={'id':'commodities-table'})
    arb_ops = pd.read_html(str(table))[0].dropna().sort_values('Profit', ascending=False).set_index('Name')
    arb_ops['link'] = arb_ops.index.map(pd.Series({x.text:x['href'] for x in table.find_all('a')}))
    return arb_ops

def get_trade_routes(arb_ops, systems, system_coords, n_commodities=10):
    """ Find the best stations to buy & sell the most arbitragable commodities """
    trade_routes = []
    for (commodity_name, commodity_details) in tqdm(arb_ops.head(n_commodities).iterrows(), total=n_commodities):
        r = req.get(f"https://eddb.io{commodity_details.link}")
        tables = BeautifulSoup(r.content, parser='lxml', features='lxml').find_all('table')
        if len(tables) != 2:
            continue
        buy_table, sell_table = tables
        buy_stations, sell_stations = [pd.read_html(str(x))[0].rename(columns={'Unnamed: 6':'latency'})  for x in [buy_table, sell_table]]
        buy_stations['station_id'] = buy_stations['Station'].map(pd.Series({x.text:x['href'] for x in buy_table.find_all('a')})).str.split('/').str[-1]
        sell_stations['station_id'] = sell_stations['Station'].map(pd.Series({x.text:x['href'] for x in sell_table.find_all('a')})).str.split('/').str[-1]
        buy_stations['coords'] = buy_stations.System.map(system_coords)
        sell_stations['coords'] = sell_stations.System.map(system_coords)
        buy_stations = buy_stations[['Station','Pad','station_id','System','Buy','Supply','coords']].rename(columns=lambda x : 'buy_'+x.lower()).rename(columns={'buy_buy':'buy_price'})
        sell_stations = sell_stations[['Station','Pad','station_id','System','Sell','Demand','coords']].rename(columns=lambda x : 'sell_'+x.lower()).rename(columns={'sell_sell':'sell_price'})
        commodity_trade_routes = pd.concat([pd.concat([x[0][1], x[1][1]]) for x in itertools.product(buy_stations.iterrows(), sell_stations.iterrows())], axis=1).T.reset_index(drop=True)
        commodity_trade_routes['commodity'] = commodity_name
        trade_routes.append(commodity_trade_routes)
    trade_routes = pd.concat(trade_routes)
    trade_routes['pad_size'] = trade_routes[['buy_pad','sell_pad']].apply(set, axis=1).apply(max)
    trade_routes['unit_profit'] = trade_routes.sell_price - trade_routes.buy_price
    trade_routes['n_avaliable_units'] = trade_routes.apply(lambda x : min(x.buy_supply, x.sell_demand), axis=1)
    trade_routes['distance'] = trade_routes.apply(lambda x : dist(x.buy_coords, x.sell_coords), axis=1)
    return trade_routes.drop(columns={'buy_pad','sell_pad'})

def get_routes(trade_routes, cargo_space, current_system, ids=False, no_return=False, jump_range=0):
    """ Calculate the best profit per distance travelled for buying & selling goods """
    start_coords = current_system[['x','y','z']].apply(lambda x : tuple(x), axis=1).iloc[0]
    trade_routes['start_leg'] = trade_routes.buy_coords.apply(lambda x : dist(x,start_coords))
    trade_routes['end_leg'] = trade_routes.sell_coords.apply(lambda x : dist(x,start_coords))

    if jump_range!=0:
        # Turn these into ~hops rather than distances
        trade_routes[['distance','start_leg','end_leg']] = np.ceil(trade_routes[['distance','start_leg','end_leg']] / jump_range)

    if no_return:
        trade_routes['loop_distance'] = trade_routes[['distance','start_leg']].apply(sum, axis=1)
    else:
        trade_routes['loop_distance'] = trade_routes[['distance','start_leg','end_leg']].apply(sum, axis=1)
    trade_routes['n_units'] = trade_routes['n_avaliable_units'].apply(lambda x : min(x, cargo_space))
    trade_routes['total_profit'] = trade_routes['n_units'] * trade_routes['unit_profit']
    trade_routes['profit_ratio'] = trade_routes['total_profit'] / trade_routes['loop_distance']
    trade_routes = trade_routes.sort_values('profit_ratio', ascending=False)
    if ids:
        return trade_routes[['commodity','buy_station','buy_system','sell_station','sell_system','buy_price','sell_price','loop_distance','pad_size','n_avaliable_units','total_profit','profit_ratio','buy_station_id','sell_station_id']]
    return trade_routes[['commodity','buy_station','buy_system','sell_station','sell_system','buy_price','sell_price','loop_distance','pad_size','n_avaliable_units','total_profit','profit_ratio']]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start_system", help="Your current system", default='LP 128-9', type=str)
    parser.add_argument("-c", "--cargo_space", help="Your avaliable cargo space", default=40, type=int)
    parser.add_argument("-nr", "--no_return", help="Do you want to return home?", action='store_true')
    parser.add_argument("-jr", "--jump_range", help="Your ships loaded jump range", default=0, type=float)
    parser.add_argument("-p", "--pad_size", help="Smallest pad you can land at", default='S', type=str)
    parser.add_argument("--n_results", help="Number of results to return", default=20, type=int)
    parser.add_argument("--n_commodities", help="Number of commodities to check", default=15, type=int)
    args = parser.parse_args()
    
    systems, system_coords = get_systems()

    current_system = systems[systems.name.str.lower()==args.start_system.lower()].copy()
    if len(current_system) != 1:
        print(current_system)
        raise ValueError("Could not find System")

    arb_ops = get_arb_ops()
    trade_routes = get_trade_routes(arb_ops, systems, system_coords, n_commodities=args.n_commodities)


    routes = get_routes(trade_routes, args.cargo_space, current_system, ids=False, no_return=args.no_return, jump_range=args.jump_range)
    routes = routes[routes.pad_size<=args.pad_size]
    routes['total_profit'] = routes['total_profit'].apply(lambda x: "{:,}".format(x))
    print(routes.head(args.n_results).to_markdown(showindex=False))