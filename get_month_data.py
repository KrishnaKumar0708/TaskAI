
!pip install slack_sdk

import time
from slack_sdk import WebClient

# Set your Slack API token
slack_token = "xoxb-5371814659108-5369260642339-ucDmZ2M37vyZBcCmgBmp9EHz"

# Set the channel or user ID where you want to send messages
channel_id = "#automatemessages"

# Set the interval in seconds between each message
interval = 30 * 24 * 60 * 60  # 1 month in seconds

# Create an instance of the Slack WebClient
client = WebClient(token=slack_token)

import pandas as pd

def send_slack_message(message):
    response = client.chat_postMessage(
        channel=channel_id,
        text=message
    )
    if response["ok"]:
        print("Message sent successfully!")
    else:
        print("Failed to send message:", response["error"])

# Read the dataset
data = pd.read_excel("/content/covid-19-state-level-data (1).xlsx")

# Convert the 'date' column to datetime
data['date'] = pd.to_datetime(data['date'])

# Extract the month from the 'date' column
data['Month'] = data['date'].dt.month_name()

# Group the data by month and state, and calculate the total deaths for each state in each month
grouped_data = data.groupby(['Month', 'state']).sum('deaths')

# Sort the grouped data by month and deaths in descending order
sorted_data = grouped_data.sort_values(['Month', 'deaths'], ascending=[True, False])

# Get the top 3 states with the highest number of deaths for each month
top_states_per_month = sorted_data.groupby(level=0).head(3)

# Get the unique months
months = top_states_per_month.index.get_level_values('Month').unique()

# Loop over the months
for month in months:
    # Get the data for the current month
    month_data = top_states_per_month.loc[month]

    # Create the message content
    message = f"Top 3 states with the highest number of COVID deaths for the month of {month}\n"
    message += f"Month - {month}\n"

    # Add the state information to the message
    for i, (state, deaths) in enumerate(month_data['deaths'].iteritems(), start=1):
        message += f"State #{i} - {state}: {int(deaths)} deaths, {deaths / data['deaths'].sum() * 100:.2f}% of total US deaths\n"

    # Send the message to Slack
    send_slack_message(message)

    # Wait until the first day of the next month
    now = pd.Timestamp.now()
    next_month = (now.month % 12) + 1
    next_year = now.year + 1 if next_month == 1 else now.year
    next_month_first_day = pd.Timestamp(year=next_year, month=next_month, day=1)
    wait_time = (next_month_first_day - now).total_seconds()
    time.sleep(wait_time)
