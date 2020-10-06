# Overview

This is a repository for intraday mid-frequency algorithmic trading framework.
This framework was developed for personal use so the data collection, database storage etc. are done as such.
This repo was created to share my personal project portfolio and the actual development happens on a separate repo.

## Main files
* `run_sudden_move_reversal_analysis_equity.py` - equity trading
* `run_sudden_move_reversal_analysis_crypto.py` - crypto (binance) trading

### Backtest

* `run_sudden_move_reversal_analysis_equity_csv.py` - equity trading
* `run_sudden_move_reversal_analysis_crypto_csv.py` - crypto (binance) trading

There are a few files of format `run_....py`, `run_..._csv.py`, which follow above pattern.

### Data

The data is collected and stored in the GCP BQ database, but as this project is mainly for my personal use, all is 
done on my personal GCP project. `sandbox_export.py` has examples to pull over the data in csv format.

## Supported Broker / Exchanges

* Equity: TD Ameritrade, Ally, Tradier
* Crypto: Binance 
 
 
## Architecture

                                                                                         
                                                                                         
                                                                                         
        ┌──────────┐               ┌───────────┐                       ┌────────────────┐
        │          │               │           │                       │                │
        │ Exchange │               │ websocket │                       │      GCP       │
        │          │──────────────▶│           │─────exports──────────▶│    BigQuery    │
        │          │               │           │                       │                │
        └──────────┘               └───────────┘                       └────────────────┘
                                         │                                      │        
                                         │                                      │        
                                         │                          ┌────downloads       
                                         │                          │                    
                                         ▼                          ▼                    
                                 ┌───────────────┐          ┌───────────────┐            
                                 │               │          │               │            
                                 │  GCP PubSub   │          │CSV file export│            
                                 │               │          │               │            
                                 └───────────────┘          └───────────────┘            
                                         │                          │                    
                                         │                          │                    
                                       live                         │                    
                                     trading                        │                    
                                         │                          │                    
                                         ▼                          │                    
                                 ┌───────────────┐              backtest                 
                                 │               │                  │                    
                                 │ trade engine  │                  │                    
                                 │               │◀─────────────────┘                    
                                 │               │                                       
                                 └───────────────┘                                       
                                         │                                               
                                      trade                                              
                                    execution                                            
                                         │                                               
                                         │                                               
                                         │                                               
                                         ▼                                               
                                 ┌───────────────┐                                       
                                 │               │                                       
                                 │  Broker API   │                                       
                                 │               │                                       
                                 └───────────────┘              


                         