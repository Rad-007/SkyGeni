import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn theme for better aesthetics
sns.set_theme(style="whitegrid", context="talk", font_scale=1.1)
plt.rcParams["figure.figsize"] = (8, 6)
plt.rcParams["savefig.dpi"] = 300

# Ensure the output directory exists
output_dir = "visuals"
os.makedirs(output_dir, exist_ok=True)

# ------------------------------
# Read CSV Files (all comma-separated)
# ------------------------------
# Financial information file (includes an 'id' column)
financial_df = pd.read_csv("finanical_information.csv", parse_dates=["start_date", "end_date"])

# Industry client details
industry_df = pd.read_csv("industry_client_details.csv")

# Payment information (convert payment_date to datetime)
payment_df = pd.read_csv("payment_information.csv")
payment_df["payment_date"] = pd.to_datetime(payment_df["payment_date"], format="%m/%d/%Y")

# Subscription information (convert dates to datetime and convert renewed to boolean)
subscription_df = pd.read_csv("subscription_information.csv")
subscription_df["start_date"] = pd.to_datetime(subscription_df["start_date"])
subscription_df["end_date"] = pd.to_datetime(subscription_df["end_date"])
subscription_df["renewed"] = subscription_df["renewed"].astype(str).str.upper() == "TRUE"

# ------------------------------
# Question 1: Count Finance Lending and Block Chain Clients
# ------------------------------
industries_of_interest = ["Finance Lending", "Block Chain"]
filtered_clients = industry_df[industry_df["industry"].isin(industries_of_interest)]
industry_counts = filtered_clients["industry"].value_counts()

print("Question 1: Number of clients by industry (Finance Lending and Block Chain):")
print(industry_counts)

# Beautified Bar Plot for Q1 using Seaborn
plt.figure()
sns.barplot(x=industry_counts.index, y=industry_counts.values,width=0.5, palette=["#69b3a2", "#e76f51"])
plt.title("Count of Finance Lending and Block Chain Clients", fontsize=18, weight="bold")
plt.xlabel("Industry", fontsize=14)
plt.ylabel("Number of Clients", fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "question1.png"))
plt.show()
plt.close()

# ------------------------------
# Question 2: Which Industry has the Highest Renewal Rate?
# ------------------------------
# Merge subscription information with industry details on client_id
merged_subscriptions = pd.merge(subscription_df, industry_df, on="client_id", how="inner")

if merged_subscriptions.empty:
    print("\nQuestion 2: No overlapping client IDs found between subscription and industry details. " 
          "Cannot compute renewal rates by industry from the provided data.")
else:
    renewal_stats = merged_subscriptions.groupby("industry")["renewed"].agg(total="count", renewed_sum="sum")
    renewal_stats["renewal_rate"] = renewal_stats["renewed_sum"] / renewal_stats["total"]
    highest_industry = renewal_stats["renewal_rate"].idxmax()
    print("\nQuestion 2: Industry with the highest renewal rate:")
    print(f"{highest_industry} with a renewal rate of {renewal_stats.loc[highest_industry, 'renewal_rate']:.2f}")
    
    # Beautified Bar Plot for Q2 using Seaborn
    plt.figure()
    sns.barplot(x=renewal_stats.index, y=renewal_stats["renewal_rate"], palette="viridis")
    plt.title("Renewal Rate by Industry", fontsize=18, weight="bold")
    plt.xlabel("Industry", fontsize=14)
    plt.ylabel("Renewal Rate", fontsize=14)
    plt.ylim(0, 1)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "question2.png"))
    plt.show()
    plt.close()

# ------------------------------
# Question 3: Average Inflation Rate when Subscriptions were Renewed
# ------------------------------
# Use the end_date of renewed subscriptions to find corresponding inflation rates
renewed_subscriptions = subscription_df[subscription_df["renewed"]]

def get_inflation_for_date(date, fin_df):
    match = fin_df[(fin_df["start_date"] <= date) & (fin_df["end_date"] >= date)]
    if not match.empty:
        return match.iloc[0]["inflation_rate"]
    else:
        return np.nan

renewed_subscriptions["inflation_rate"] = renewed_subscriptions["end_date"].apply(
    lambda d: get_inflation_for_date(d, financial_df)
)
avg_inflation = renewed_subscriptions["inflation_rate"].mean()

if np.isnan(avg_inflation):
    print("\nQuestion 3: No matching financial information periods found for the renewed subscription dates. "
          "Cannot compute average inflation rate from the provided data.")
else:
    print("\nQuestion 3: Average inflation rate for renewed subscriptions:")
    print(avg_inflation)

# ------------------------------
# Question 4: Median Amount Paid Each Year for All Payment Methods
# ------------------------------
payment_df["year"] = payment_df["payment_date"].dt.year
median_paid = payment_df.groupby("year")["amount_paid"].median()

print("\nQuestion 4: Median amount paid each year:")
print(median_paid)

# Beautified Bar Plot for Q4 using Seaborn
plt.figure()
sns.barplot(x=median_paid.index.astype(str), y=median_paid.values, palette="mako")
plt.title("Median Amount Paid per Year", fontsize=18, weight="bold")
plt.xlabel("Year", fontsize=14)
plt.ylabel("Median Amount Paid", fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "question4.png"))
plt.show()
plt.close()
