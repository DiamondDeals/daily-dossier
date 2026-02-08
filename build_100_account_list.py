#!/usr/bin/env python3
"""
Build comprehensive 100-account list:
- 92 from AI list
- 8+ top entrepreneur/founders
"""
import json

# Load the AI list
with open('twitter_vetted_accounts.json', 'r') as f:
    ai_list = json.load(f)

ai_accounts = [acc['username'] for acc in ai_list['accounts']]

# Top entrepreneurs/founders to add (not in AI list)
additional_founders = [
    # Top indie hackers with public revenue
    "dannypostmaa",    # Prototypr, $15K/MRR, shares revenue openly
    "marc_louvion",    # Multiple products, transparent revenue
    "yongfook",        # Bannerbear founder, $30K/MRR
    "thepatwalls",     # Indie hacker, transparent revenue
    "petecodes",       # No-code founder, shares journey
    "matgomez",        # Product hunt maker, transparent
    "daanbrits",       # Side project founder
    "dvassallo",       # Ex-Amazon, indie hacker
    
    # SaaS founders with known exits/revenue
    "paulg",           # Y Combinator (if not in list)
    "patio11",         # Patrick McKenzie, Stripe
    "Suhail",          # Mixpanel founder
    "dhh",             # Basecamp/Hey founder
    "jasonfried",      # Basecamp co-founder
    "naval",           # AngelList, philosopher
    "sama",            # OpenAI, YC
    
    # Bootstrapped SaaS success
    "shl",             # Gumroad founder
    "robwalling",      # TinySeed, MicroConf
    "mijustin",        # Transistor.fm
    "ajlkn",           # HTML5 UP, maker
    "levie",           # Box CEO
]

print("=" * 70)
print("BUILDING 100-ACCOUNT MONITORING LIST")
print("=" * 70)

print(f"\n✅ Starting with {len(ai_accounts)} accounts from AI list")
print(f"➕ Adding {len(additional_founders)} top entrepreneur/founder accounts")

# Combine (filter out duplicates)
all_accounts = list(set(ai_accounts + additional_founders))

print(f"\n📊 Total unique accounts: {len(all_accounts)}")

# Save to monitoring config
config = {
    "version": "1.0",
    "created": "2026-02-07",
    "total_accounts": len(all_accounts),
    "sources": {
        "ai_list_1219117707150233605": len(ai_accounts),
        "manual_entrepreneur_additions": len(additional_founders)
    },
    "accounts": sorted(all_accounts),
    "notes": "Top 100 AI builders, indie hackers, and successful founders with public revenue"
}

with open('twitter_monitoring_accounts.json', 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ Saved to: twitter_monitoring_accounts.json")

# Show categories
print("\n" + "=" * 70)
print("ACCOUNT BREAKDOWN")
print("=" * 70)

# Revenue sharing founders
revenue_founders = ["marclou", "levelsio", "dannypostmaa", "yongfook"]
print(f"\n💰 Revenue-sharing founders ({len(revenue_founders)}):")
for acc in revenue_founders:
    if acc in all_accounts:
        print(f"   @{acc}")

# Known exits
exit_founders = ["dhh", "jasonfried", "Suhail", "shl", "patio11"]
print(f"\n🚀 Known exits/big success ({len(exit_founders)}):")
for acc in exit_founders:
    if acc in all_accounts:
        print(f"   @{acc}")

# AI company founders
ai_founders = ["sama", "OpenAI", "AnthropicAI", "GoogleDeepMind"]
print(f"\n🤖 AI company founders ({len(ai_founders)}):")
for acc in ai_founders:
    if acc in all_accounts:
        print(f"   @{acc}")

print("\n" + "=" * 70)
print(f"✅ {len(all_accounts)} accounts ready for monitoring")
print("=" * 70)
