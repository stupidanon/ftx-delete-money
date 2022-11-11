import ccxt
from rich import print
from rich.prompt import Prompt

"Your API key from FTX, make sure it has full permissions and is not read-only!"
"Your secret key from FTX, make sure it has full permissions and is not read-only!"


print(
    "[bold]This program will attempt to [red underline]delete[/red underline] your FTX balance. \nAre you sure you wish to proceed? \n(The creator of this app will not be held liable, this is your final warning!)[/bold]"
)

if Prompt.ask("Do you wish to proceed?", choices=["Yes", "No"]) == "No":
    quit()

print(
    "[bold red]Before running this, move all funds to the main account from any sub-accounts[/bold red]"
)

api = Prompt.ask("Please enter your FTX API key")
secret = Prompt.ask("Please enter your FTX secret key")
print("[bold]The keys:[/]", api, secret)

ftx = ccxt.ftx(
    {
        'apiKey': api,
        'secret': secret,
    }
)

# Assert working keys
try:
    print(f"Account balance: { ftx.fetch_balance() }")
except:
    print("[bold red]Invalid API or secret key[/bold red]")
    print("[bold red]Please try again, shutting down![/bold red]")
    exit()

if Prompt.ask("Do you wish to proceed? Final warning!", choices=["Yes", "No"]) == "No":
    quit()

ftx.load_markets()

print("[bold]Attempting to set max leverage[/]")
response = ftx.private_post_account_leverage(
    {
        "leverage": 20,
    }
)


# Buy function
def buy(amount):
    symbol = "BTC/USD:USD"  # change for your symbol
    type = "market"
    side = "buy"
    price = None
    params = {"reduceOnly": False}
    order = ftx.create_order(symbol, type, side, amount, price, params)
    print("[italic]Bought BTC[/italic]")


# Close function
def close_position():
    symbol = "BTC/USD:USD"  # change for your symbol
    positions = ftx.fetch_positions()
    positions_by_symbol = ftx.index_by(positions, "symbol")
    if symbol in positions_by_symbol:
        position = positions_by_symbol[symbol]
        type = "market"
        side = "sell" if position["side"] == "long" else "buy"
        amount = position["contracts"]
        price = None
        params = {"reduceOnly": True}
        try:
            order = ftx.create_order(symbol, type, side, amount, price, params)
            print("[italic]Closed position[/italic]")
        except Exception as e:
            print(e)
            print("[bold red]Error closing position, see error above[/bold red]")
    else:
        print("You do not have an open", symbol, "position")


# Run the main algorithm to delete the balance
# Market buy USDT-USD and then instantly sell it
while True:
    # Get the max size you can trade with
    bal = ftx.fetch_balance()["USD"]["free"]
    free_usd = bal * 19
    print(f"Current USD balance: {free_usd}")
    # Market buy USDT-USD with max size
    price_ask = ftx.fetch_ticker("BTC/USD:USD")["ask"]
    buy(free_usd / price_ask - 0.001)
    # Close position
    close_position()
