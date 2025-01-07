# Money Rhythm - A Zero Based Budget App

A Django-based budgeting application that helps users manage their finances using zero-based budgeting principles. The app integrates with Plaid API for automatic transaction imports and provides flexible budget periods based on user pay cycles.

## Features

- **Custom Budget Periods**: Create budgets based on your pay cycle instead of traditional monthly periods
- **Zero-Based Budgeting**: Every dollar has a job - plan your spending to zero
- **Bank Integration**: Connect with your bank accounts via Plaid API for automatic transaction imports
- **Shared Budgets**: Collaborate on household finances while maintaining separate personal budgets
- **Bill Calendar**: Track and manage recurring expenses
- **Dynamic Categories**: Create and customize spending categories
- **Real-Time Adjustments**: Move money between categories as needed
- **Transaction Tracking**: Automatic import and categorization of transactions
- **Secure Authentication**: Custom user model with email-based authentication

## Technical Stack

- **Backend**: Django 5.1.4
- **Frontend**: TailwindCSS 3.8.0
- **API Integration**: Plaid API (via plaid-python 28.0.0)
- **HTTP Client**: HTTPX 0.28.1

## Prerequisites

- Python 3.10+
- pip
- Node.js and npm (for TailwindCSS)