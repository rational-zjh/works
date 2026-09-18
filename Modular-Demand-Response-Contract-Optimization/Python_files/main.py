import numpy as np

import grid
import agent
import contract
import matplotlib.pyplot as plt
import time
import statistics
import pandas as pd
from datetime import datetime
import random as rd


def main():
    # 设置相同随机种子
    np.random.seed(123)
    for i in range(1):
        M = 1000
        number_of_agents = 200
        number_of_simulation_per_lanbda = 100
        generator_price_multiply = 1
        gamma = [1.0,1.166,1.333,1.5,1.666,1.833,2]
        df_columns = ['actuel expanse','gamma','M','actuel kWh reduced','Met the demand']
        row_data_df = pd.DataFrame(columns=df_columns)

        Fixed_cont_avg_cost = []
        Fixed_cont_avg_reliability = []
        Fixed_single_cont_avg_cost = []
        Fixed_single_cont_avg_reliability = []
        T_F_List_Fixed_cont_Met_the_demand = []
        Fixed_cont_Total_expense = []
        gamma_used = []
        for lb in gamma:
            Fixed_cont_reduce_list = []
            for i in range(number_of_simulation_per_lanbda):
                start = time.time()
                print('iteration:',i)
                Grid = grid.grid(M,lb)
                Grid.introduce_self()
                Agents = []

                for num in range(number_of_agents):
                    ag = agent.agent(num)
                    Agents.append(ag)


                Contracts = []
                for i in range(10, M+1, 10):
                    Contracts.append(contract.contract(i,0.3,0.5))


                single_contract = []
                single_contract.append(contract.contract(50,0.3,0.5))

                Grid.set_single_contract(single_contract)
                Grid.set_contract(Contracts)
                Grid.set_agents(Agents)
                Grid.send_contrects_to_agents()
                Grid.send_single_contrects_to_agents()


                for ag in Agents:
                    ag.Fixed_cont_bid_on_contract()


                for ag in Agents:
                    ag.Fixed_single_cont_bid_on_contract()

                Grid.Fixed_cont_get_bids_from_agent()
                Grid.Fixed_cont_generator_bids(price_multiply=generator_price_multiply)
                Grid.Fixed_cont_get_q_from_agent()
                Fixed_cont_sum_of_bids = Grid.knapsack(bids_type='Fixed_cont')
                Grid.Fixed_cont_pay_to_agents(Fixed_cont_sum_of_bids)
                Grid.Fixed_cont_reliability()
                Grid.Fixed_single_cont_get_bids_from_agent()
                Grid.Fixed_single_cont_get_q_from_agent()


                Fixed_cont_Total_expense.append(Grid.Fixed_cont_Total_expense_sum)
                Fixed_cont_reduce_list.append(Grid.Fixed_cont_reliability_sum_q)
                if Grid.Fixed_cont_reliability_sum_q >= Grid.M:
                    met_the_demand = 1
                else:
                    met_the_demand = 0
                T_F_List_Fixed_cont_Met_the_demand.append(met_the_demand)
                print('Fixed_cont- Met_the_demand: ', T_F_List_Fixed_cont_Met_the_demand)
                print('Fixed_cont- Total_expense: ', Fixed_cont_Total_expense)
                gamma_used.append(lb)
                row_data_df = row_data_df._append(pd.DataFrame(
                                                 {'actuel expanse':[Grid.Fixed_cont_Total_expense_sum],
                                                  'gamma':[lb],
                                                  'M': [M],
                                                  'actuel kWh reduced': [Grid.Fixed_cont_reliability_sum_q],
                                                  'Met the demand': [met_the_demand]}))
                end = time.time()
                print('iteration took:', (end - start), 'sec')
                print('-'*200)
            Fixed_cont_avg_cost.append(statistics.mean(Fixed_cont_Total_expense))
            if len(T_F_List_Fixed_cont_Met_the_demand) > 0:
                Fixed_cont_avg_reliability.append(T_F_List_Fixed_cont_Met_the_demand.count(True) / len(T_F_List_Fixed_cont_Met_the_demand))
            else:
                Fixed_cont_avg_reliability.append(0.0)

        filename = datetime.now().strftime('./energy_demamd_row_data-%Y-%m-%d-%H-%M-%S.csv')
        print(Fixed_cont_avg_reliability)
        row_data_df.to_csv(filename,index=False)
        graph_it(Fixed_cont_avg_reliability,
                 Fixed_single_cont_avg_reliability, Fixed_cont_avg_cost,
                 Fixed_single_cont_avg_cost)

def graph_it(Fixed_cont_avg_reliability =[],
             Fixed_single_cont_avg_reliability=[],
             Fixed_cont_avg_cost=[],
             Fixed_single_cont_avg_cost=[]):
    plt.rcParams["figure.figsize"] = (8, 8)
    fig, ax = plt.subplots()

    ax.plot(Fixed_cont_avg_reliability, Fixed_cont_avg_cost, color='blue',marker='o',label="fixed multiple cont")
    ax.plot(Fixed_single_cont_avg_reliability, Fixed_single_cont_avg_cost, color='black',marker='o', label="fixed single cont")
    ax.set(xlabel="Total_Reliability", ylabel="expenses ($)", title="(a)n= 200")
    fig.savefig("test.png")



if __name__ == "__main__":
    main()
    plt.show()