import random as rd
from math import inf
import generator

class grid:
    def __init__(self, M, gama):
        self.M = M
        self.gama = gama
        print('The grid what to reduce: ', self.M, 'kWh')
        print("The grid ask to reduce", self.M * self.gama, "kWh")


    def introduce_self(self):
        print("The grid ask to reduce", self.M * self.gama, "kWh")

    def set_contract(self, contract):
        self.contract = contract

    def set_single_contract(self, single_contract):
        self.single_contract = single_contract

    def set_agents(self,agents):
        self.agents = agents

    def send_contrects_to_agents(self):
        for ag in self.agents:
            ag.set_contract(self.contract)

    def send_single_contrects_to_agents(self):
        for ag in self.agents:
            ag.set_single_contract(self.single_contract)

    def Fixed_cont_generator_bids(self, price_multiply=0.5):
        self.generators =[]
        i = -1
        for _ in range(4):
            self.generators.append(generator.generator(i, 5000, price_multiply))
            i-=1
        for _ in range(4):
            self.generators.append(generator.generator(i, 1000, price_multiply))
            i-=1
        for _ in range(2):
            self.generators.append(generator.generator(i, 500, price_multiply))
            i-=1
        for _ in range(4):
            self.generators.append(generator.generator(i, 100, price_multiply))
            i -= 1
        for _ in range(2):
            self.generators.append(generator.generator(i, 50, price_multiply))
            i -= 1
        for _ in range(5):
            self.generators.append(generator.generator(i, 10, price_multiply))
            i -= 1


    def Cliff_cont_get_bids_from_agent(self):
        self.Cliff_cont_bids_dict = dict()
        for ag in self.agents:
            self.Cliff_cont_bids_dict[ag.ID] = ag.Cliff_cont_bids

    def Cliff_cont_get_q_from_agent(self):
        self.Cliff_cont_q_dict = dict()
        for ag in self.agents:
            self.Cliff_cont_q_dict[ag.ID] = ag.Cliff_cont_all_q

    def Fixed_single_cont_get_bids_from_agent(self):
        self.Fixed_single_cont_bids_dict = dict()
        for ag in self.agents:
            self.Fixed_single_cont_bids_dict[ag.ID] = ag.Fixed_single_cont_bids

    def Fixed_single_cont_get_q_from_agent(self):
        self.Fixed_single_cont_q_dict = dict()
        for ag in self.agents:
            self.Fixed_single_cont_q_dict[ag.ID] = ag.Fixed_single_cont_all_q

    def Fixed_cont_get_bids_from_agent(self):
        self.Fixed_cont_bids_dict = dict()
        for ag in self.agents:
            self.Fixed_cont_bids_dict[ag.ID] = ag.Fixed_cont_bids
        #print(self.bids_dict)

    def Fixed_cont_get_q_from_agent(self):
        self.Fixed_cont_q_dict = dict()
        for ag in self.agents:
            self.Fixed_cont_q_dict[ag.ID] = ag.Fixed_cont_all_q

    def select_SCE_agents(self):
        self.selected_SCE_agents = []
        m_SCE = 0
        for ag in self.agents:
            if m_SCE >= self.M * self.gama:
                break
            #if ag.bid_in_SCE < 0.5:
            if ag.c / ag.q <= 0.5:
                self.selected_SCE_agents.append(ag)
                m_SCE += ag.q
        if m_SCE < self.M * self.gama:
            self.Use_reserve_price = ((self.M * self.gama) - m_SCE) * 0.5
            self.Use_reserve_wt = ((self.M * self.gama) - m_SCE)
        else:
            self.Use_reserve_price = 0
            self.Use_reserve_wt = 0


    def SCE_Total_Expenses(self):
        self.List_SCE_pay = []
        self.List_actually_SCE_reduce = []
        #cont = self.contract[0]
        for ag in self.selected_SCE_agents:
            cont_l = ag.SCE_cont_l_of_selected_cont
            SCE_cont_random_number = rd.uniform(0, 1)
            if ag.p >= SCE_cont_random_number:
                if ag.q < 0.5 * cont_l: #ag.l_of_selected_cont
                    Agents_SCE_pay = 0
                    self.List_SCE_pay.append(Agents_SCE_pay)
                elif ag.q <= 1.5 * cont_l and ag.q >= 0.5 * cont_l: #ag.l_of_selected_cont
                    Agents_SCE_pay = 0.5 * ag.q
                    self.List_SCE_pay.append(Agents_SCE_pay)
                    self.List_actually_SCE_reduce.append(ag.q)
                elif ag.q > 1.5 * cont_l: #ag.l_of_selected_cont
                    Agents_SCE_pay = 0.5 * 1.5 * ag.q
                    self.List_SCE_pay.append(Agents_SCE_pay)
                    self.List_actually_SCE_reduce.append(ag.q)
        self.sum_of_list_SCE_pay = (sum(self.List_SCE_pay)) + self.Use_reserve_price
        self.sum_List_actually_SCE_reduce = sum(self.List_actually_SCE_reduce) + self.Use_reserve_wt

    def SCE_reliability(self):
        if self.sum_List_actually_SCE_reduce >= self.M:
            print('SCE- The grid met the demand')
        else:
            print('SCE- The grid doesn\'t met the demand')


    def Fixed_cont_knapsack(self, agents = None):
        if agents is None:
            agents = self.agents
        min_cont = self.contract[0]
        if self.M * self.gama % min_cont.l == 0:
            W = int(self.M * self.gama)
        else:
            W = int(round((self.M * self.gama) / min_cont.l) * min_cont.l)
        wt = []
        Knapsack_agents_map = []
        i = 0
        val = []
        for ag in agents:
            if ag.Fixed_cont_bids[0] is not None:
                val.append(ag.Fixed_cont_bids[0])
                Knapsack_agents_map.append((i,ag.ID))
                i += 1

        for gen in self.generators:
            val.append(gen.bid)
            Knapsack_agents_map.append((i, gen.ID))
            i += 1

        n = len(val)
        for index, id in Knapsack_agents_map:
            if id >= 0:
                wt.append(self.agents[id].Fixed_cont_l_of_selected_cont)
            else:
                wt.append(self.generators[-(id) -1].l)


        # wt = [ag.l for ag in self.agents]
        K = [[0 for w in range(W + 1)]
             for i in range(n + 1)]

        # fill 0th row with infinity
        for i in range(W + 1):
            K[0][i] = inf

            # fill 0th column with 0
        for i in range(1, n + 1):
            K[i][0] = 0

        Used = [[False for w in range(W + 1)]
                for i in range(n + 1)]

        for i in range(1, n + 1):
            for w in range(1, W + 1):
                if wt[i - 1] > w:
                    K[i][w] = K[i - 1][w]
                else:
                    if K[i][w - wt[i - 1]] + val[i - 1] < K[i - 1][w]:
                        if Used[i][w - wt[i - 1]] == False:
                            K[i][w] = K[i][w - wt[i - 1]] + val[i - 1]
                            Used[i][w] = True
                        else:
                            K[i][w] = K[i - 1][w]
                    else:
                        K[i][w] = K[i - 1][w]
        #for i in range(n + 1):
        #    print(K[i])
        Fixed_cont_optimal_set_before = []
        w = W
        for i in range(n, -1, -1):
            if w == 0:
                break
            elif i == 0 and K[i][w] != 0:
                Fixed_cont_optimal_set_before.insert(0, i - 1)
            elif K[i][w] != K[i - 1][w]:
                Fixed_cont_optimal_set_before.insert(0, i - 1)
                w -= wt[i - 1]
        self.Fixed_cont_optimal_set_after = []
        for row in Fixed_cont_optimal_set_before:
            for index, ag_id in Knapsack_agents_map:
                if row == index:
                    self.Fixed_cont_optimal_set_after.append(ag_id)
        #print('The optimal set is ', self.optimal_set_after)
        Fixed_cont_sum_of_bids = 0
        for i in self.Fixed_cont_optimal_set_after:
            if i >= 0:
                Fixed_cont_sum_of_bids += self.agents[i].Fixed_cont_bids[0]
            else:
                Fixed_cont_sum_of_bids += self.generators[-(i) - 1].bid
        return Fixed_cont_sum_of_bids

    def Fixed_cont_pay_to_agents(self, Fixed_cont_sum_of_bids):
        self.Fixed_cont_Total_expense_sum = 0
        for i in self.Fixed_cont_optimal_set_after:
            if i >= 0:
                Fixed_cont_agents_without_agent_i = self.agents[:i]+self.agents[i+1:]
                Fixed_cont_optimal_sum_of_bids_without_agent_i = self.knapsack(agents=Fixed_cont_agents_without_agent_i, bids_type = 'Fixed_cont')
                Fixed_cont_original_sum_of_bids_without_agent_i = Fixed_cont_sum_of_bids - self.agents[i].Fixed_cont_bids[0]
                Fixed_cont_payment_to_agnet = Fixed_cont_optimal_sum_of_bids_without_agent_i - Fixed_cont_original_sum_of_bids_without_agent_i
                self.Fixed_cont_Total_expense_sum += Fixed_cont_payment_to_agnet
            else:
                Fixed_cont_payment_to_generator = self.generators[-i-1].bid
                self.Fixed_cont_Total_expense_sum += Fixed_cont_payment_to_generator



    def Fixed_cont_reliability(self):
        self.Fixed_cont_reliability_agents_q = []
        #self.Fixed_cont_reliability_agents_q.append(self.Fixed_cont_Use_reserve_q)
        for id in self.Fixed_cont_optimal_set_after:
            if id >= 0:
                Fixed_cont_random_number = rd.uniform(0, 1)
                if self.agents[id].p >= Fixed_cont_random_number:
                    self.Fixed_cont_reliability_agents_q.append(self.agents[id].q)
                #agent pays the contrect f
                else:
                    self.Fixed_cont_Total_expense_sum -= self.agents[id].Fixed_cont_f_of_selected_cont
            else:
                self.Fixed_cont_reliability_agents_q.append(self.generators[-id-1].l)
        #print('The reliable agents reduce :', self.reliability_agents_q)
        self.Fixed_cont_reliability_sum_q = sum(self.Fixed_cont_reliability_agents_q)
        print('Fixed cont- The reliabel sum of q in optimal set is: ', self.Fixed_cont_reliability_sum_q, 'KWh')
        #print('The sum of reliability agents is: ', self.Fixed_cont_reliability_sum_q)
        if self.Fixed_cont_reliability_sum_q >= self.M:
            print('Fixed cont- The grid met the demand')
        else:
            print('Fixed cont- The grid doesn\'t met the demand')

    def  knapsack(self, agents=None, bids_type='Cliff_cont_bids'):
        if agents is None:
            agents = self.agents
        min_cont = self.contract[0]
        single_cont = self.single_contract[0]
        #if bids_type == 'Fixed_cont' or bids_type == 'Cliff_cont_bids':
        #    W = self.round_w(min_cont.l)
        #elif bids_type=='Fixed_single_cont':
        #    W = self.round_w(single_cont.l)
        W = self.round_w(single_cont.l)
        wt = []
        Knapsack_agents_map = {}
        i = 0
        val = []
        if bids_type == 'Cliff_cont_bids':
            for ag in agents:
                if ag.Cliff_cont_bids[0] is not None:
                    val.append(ag.Cliff_cont_bids[0])
                    Knapsack_agents_map[i] = ag.ID
                    i += 1
        elif bids_type == 'Fixed_cont':
            for ag in agents:
                if ag.Fixed_cont_bids[0] is not None:
                    val.append(ag.Fixed_cont_bids[0])
                    Knapsack_agents_map[i] = ag.ID
                    i += 1
        elif bids_type=='Fixed_single_cont':
            for ag in agents:
                if ag.Fixed_single_cont_bids[0] is not None:
                    val.append(ag.Fixed_single_cont_bids[0])
                    Knapsack_agents_map[i] = ag.ID
                    i += 1



        for gen in self.generators:
            val.append(gen.bid)
            Knapsack_agents_map[i] = gen.ID
            i += 1

        n = len(val)
        for id in Knapsack_agents_map.values():
            if id >= 0:
                if bids_type == 'Cliff_cont_bids':
                    wt.append(self.agents[id].Cliff_cont_l_of_selected_cont)
                elif bids_type == 'Fixed_cont':
                    wt.append(self.agents[id].Fixed_cont_l_of_selected_cont)
                elif bids_type == 'Fixed_single_cont':
                    wt.append(self.agents[id].Fixed_single_cont_l_of_selected_cont)
            else:
                wt.append(self.generators[-(id) -1].l)


        # wt = [ag.l for ag in self.agents]
        K = [[0 for w in range(0,W + 1,10)]
             for i in range(n + 1)]

        # fill 0th row with infinity
        for i in range(len(K[0])):
            K[0][i] = inf

            # fill 0th column with 0
        for i in range(1, n + 1):
            K[i][0] = 0

        Used = [[False for w in range(0,W + 1,10)]
                for i in range(n + 1)]

        for i in range(1, n + 1):
            for w in range(10,W + 1,10):
                w_loc = w//10
                agent_wt_loc = wt[i - 1]//10
                if wt[i - 1] > w:
                    K[i][w_loc] = K[i - 1][w_loc]
                else:
                    if K[i][w_loc - agent_wt_loc] + val[i - 1] < K[i - 1][w_loc]:
                        if Used[i][w_loc - agent_wt_loc] == False:
                            K[i][w_loc] = K[i][w_loc - agent_wt_loc] + val[i - 1]
                            Used[i][w_loc] = True
                        else:
                            K[i][w_loc] = K[i - 1][w_loc]
                    else:
                        K[i][w_loc] = K[i - 1][w_loc]
        #for i in range(n + 1):
        #    print(K[i])
        optimal_set_before = []
        w = W//10
        for i in range(n, 0, -1):
            if w == 0:
                break
            elif i == 0 and K[i][w] != 0:
                optimal_set_before.insert(0, i - 1)
            elif K[i][w] != K[i - 1][w]:
                optimal_set_before.insert(0, i - 1)
                w -= wt[i - 1]//10
        optimal_set_after = []
        for row in optimal_set_before:
            try:
                optimal_set_after.append(Knapsack_agents_map[row])
            except:
                print('error')
            #Knapsack_agents_map
            #for index, ag_id in Knapsack_agents_map:
                #    if row == index:
            #        self.Cliff_cont_optimal_set_after.append(ag_id)
        #print('The optimal set is ', self.optimal_set_after)
        sum_of_bids = 0
        for i in optimal_set_after:
            if i >= 0:
                if bids_type == 'Cliff_cont_bids':
                    sum_of_bids += self.agents[i].Cliff_cont_bids[0]
                elif bids_type == 'Fixed_cont':
                    sum_of_bids += self.agents[i].Fixed_cont_bids[0]
                elif bids_type == 'Fixed_single_cont':
                    sum_of_bids += self.agents[i].Fixed_single_cont_bids[0]
            else:
                sum_of_bids += self.generators[-(i) - 1].bid

        if bids_type == 'Cliff_cont_bids':
            self.Cliff_cont_optimal_set_after = optimal_set_after
        elif bids_type == 'Fixed_cont':
            self.Fixed_cont_optimal_set_after = optimal_set_after
        elif bids_type == 'Fixed_single_cont':
            self.Fixed_single_cont_optimal_set_after = optimal_set_after

        return sum_of_bids

    def round_w(self,l):
        if self.M * self.gama % l == 0:
            W = int(self.M * self.gama)
        else:
            W = int(round((self.M * self.gama) / l) * l)
        return W

    def Cliff_cont_pay_to_agents_2(self, Cliff_cont_sum_of_bids):
        self.Cliff_cont_Total_expense_sum = 0
        for i in self.Cliff_cont_optimal_set_after:
            if i >= 0:
                Cliff_cont_agents_without_agent_i = self.agents[:i]+self.agents[i+1:]
                Cliff_cont_optimal_sum_of_bids_without_agent_i = self.knapsack(agents=Cliff_cont_agents_without_agent_i,bids_type='Cliff_cont_bids')
                Cliff_cont_original_sum_of_bids_without_agent_i = Cliff_cont_sum_of_bids - self.agents[i].Cliff_cont_bids[0]
                Cliff_cont_payment_to_agnet = Cliff_cont_optimal_sum_of_bids_without_agent_i - Cliff_cont_original_sum_of_bids_without_agent_i
                self.Cliff_cont_Total_expense_sum += Cliff_cont_payment_to_agnet
            else:
                Fixed_cont_payment_to_generator = self.generators[-i-1].bid
                self.Cliff_cont_Total_expense_sum += Fixed_cont_payment_to_generator



    def Cliff_cont_pay_to_agents(self):
        Cliff_cont_sum_all_bids = sum([sum(filter(None,x)) for x in self.Cliff_cont_bids_dict.values()])
        print('Cliff cont: The sum all of the bids is ',Cliff_cont_sum_all_bids, '$')
        Cliff_cont_sum_all_q = sum([sum(filter(None, x)) for x in self.Cliff_cont_q_dict.values()])
        print('Cliff cont: The sum all of the relevant q is ', Cliff_cont_sum_all_q, 'KWh')
        self.Cliff_cont_sum_of_bids_in_optimal_set = 0

        #for id in self.optimal_set_after:

        for num in self.Cliff_cont_optimal_set_after:
            for key, value in self.Cliff_cont_bids_dict.items():
                if key == num:
                    print(value)
                    self.Cliff_cont_sum_of_bids_in_optimal_set += value[0]
        print('Cliff cont- The sum of bids in optimal set is ', self.Cliff_cont_sum_of_bids_in_optimal_set, '$')
        self.Cliff_cont_Total_expense = []
        Cliff_cont_q_in_optimal_set = []
        for num in self.Cliff_cont_optimal_set_after:
            Cliff_cont_q_in_optimal_set.append(self.agents[num].q)
        self.Cliff_cont_Total_q_in_optimal_set = sum(Cliff_cont_q_in_optimal_set)
        print('Cliff cont- The sum of q in optimal set is: ', self.Cliff_cont_Total_q_in_optimal_set, 'KWh')
        for i in self.Cliff_cont_optimal_set_after:
            Cliff_cont_r = (Cliff_cont_sum_all_bids - self.agents[i].Cliff_cont_bids[0]) - (self.Cliff_cont_sum_of_bids_in_optimal_set - self.agents[i].Cliff_cont_bids[0])
            self.Cliff_cont_Total_expense.append(Cliff_cont_r)
        self.Cliff_cont_Total_expense_sum = int(sum(self.Cliff_cont_Total_expense)) - self.Cliff_cont_sum_of_bids_in_optimal_set
        #print('Total payment of the Grid is ', self.Total_expense_sum, '$')

    def Cliff_cont_reliability(self):
        self.Cliff_cont_reliability_agents_q = []
        #self.Cliff_cont_reliability_agents_q.append(self.Cliff_cont_Use_reserve_q)
        for id in self.Cliff_cont_optimal_set_after:
            if id >= 0:
                Cliff_cont_random_number = rd.uniform(0, 1)
                if self.agents[id].p >= Cliff_cont_random_number:
                    self.Cliff_cont_reliability_agents_q.append(self.agents[id].q)
                #agent pays the contrect f
                else:
                    self.Cliff_cont_Total_expense_sum -= self.agents[id].Cliff_cont_f_of_selected_cont
            else:
                self.Cliff_cont_reliability_agents_q.append(self.generators[-id-1].l)
        #print('The reliable agents reduce :', self.reliability_agents_q)
        self.Cliff_cont_reliability_sum_q = sum(self.Cliff_cont_reliability_agents_q)
        print('Cliff cont- The reliabel sum of q in optimal set is: ', self.Cliff_cont_reliability_sum_q, 'KWh')
        #print('The sum of reliability agents is: ', self.Cliff_cont_reliability_sum_q)
        if self.Cliff_cont_reliability_sum_q >= self.M:
            print('Cliff cont- The grid met the demand')
        else:
            print('Cliff cont- The grid doesn\'t met the demand')

    def Fixed_single_cont_knapsack(self, agents = None):
        if agents is None:
            agents = self.agents
        min_cont = self.single_contract[0]  #oded
        if self.M * self.gama % min_cont.l == 0:
            W = int(self.M * self.gama)
        else:
            W = int(round((self.M * self.gama) / min_cont.l) * min_cont.l)
        wt = []
        Knapsack_agents_map = []
        i = 0
        val = []
        for ag in agents:
            if ag.Fixed_single_cont_bids[0] is not None:
                val.append(ag.Fixed_single_cont_bids[0])
                Knapsack_agents_map.append((i,ag.ID))
                i += 1

        for gen in self.generators:
            val.append(gen.bid)
            Knapsack_agents_map.append((i, gen.ID))
            i += 1

        n = len(val)
        for index, id in Knapsack_agents_map:
            if id >= 0:
                wt.append(self.agents[id].Fixed_single_cont_l_of_selected_cont)
            else:
                wt.append(self.generators[-(id) -1].l)


        # wt = [ag.l for ag in self.agents]
        K = [[0 for w in range(W + 1)]
             for i in range(n + 1)]

        # fill 0th row with infinity
        for i in range(W + 1):
            K[0][i] = inf

            # fill 0th column with 0
        for i in range(1, n + 1):
            K[i][0] = 0

        Used = [[False for w in range(W + 1)]
                for i in range(n + 1)]

        for i in range(1, n + 1):
            for w in range(1, W + 1):
                if wt[i - 1] > w:
                    K[i][w] = K[i - 1][w]
                else:
                    if K[i][w - wt[i - 1]] + val[i - 1] < K[i - 1][w]:
                        if Used[i][w - wt[i - 1]] == False:
                            K[i][w] = K[i][w - wt[i - 1]] + val[i - 1]
                            Used[i][w] = True
                        else:
                            K[i][w] = K[i - 1][w]
                    else:
                        K[i][w] = K[i - 1][w]
        #for i in range(n + 1):
        #    print(K[i])
        Fixed_single_cont_optimal_set_before = []
        w = W
        for i in range(n, -1, -1):
            if w == 0:
                break
            elif i == 0 and K[i][w] != 0:
                Fixed_single_cont_optimal_set_before.insert(0, i - 1)
            elif K[i][w] != K[i - 1][w]:
                Fixed_single_cont_optimal_set_before.insert(0, i - 1)
                w -= wt[i - 1]
        self.Fixed_single_cont_optimal_set_after = []
        for row in Fixed_single_cont_optimal_set_before:
            for index, ag_id in Knapsack_agents_map:
                if row == index:
                    self.Fixed_single_cont_optimal_set_after.append(ag_id)
        #print('The optimal set is ', self.optimal_set_after)
        Fixed_single_cont_sum_of_bids = 0
        for i in self.Fixed_single_cont_optimal_set_after:
            if i >= 0:
                Fixed_single_cont_sum_of_bids += self.agents[i].Fixed_single_cont_bids[0]
            else:
                Fixed_single_cont_sum_of_bids += self.generators[-(i) - 1].bid
        return Fixed_single_cont_sum_of_bids

    def Fixed_single_cont_pay_to_agents_2(self, Fixed_single_cont_sum_of_bids):
        self.Fixed_single_cont_Total_expense_sum = 0
        for i in self.Fixed_single_cont_optimal_set_after:
            if i >= 0:
                Fixed_single_cont_agents_without_agent_i = self.agents[:i]+self.agents[i+1:]
                Fixed_single_cont_optimal_sum_of_bids_without_agent_i = self.knapsack(agents=Fixed_single_cont_agents_without_agent_i,bids_type='Fixed_single_cont')
                Fixed_single_cont_original_sum_of_bids_without_agent_i = Fixed_single_cont_sum_of_bids - self.agents[i].Fixed_single_cont_bids[0]
                Fixed_single_cont_payment_to_agnet = Fixed_single_cont_optimal_sum_of_bids_without_agent_i - Fixed_single_cont_original_sum_of_bids_without_agent_i
                self.Fixed_single_cont_Total_expense_sum += Fixed_single_cont_payment_to_agnet
            else:
                Fixed_single_cont_payment_to_generator = self.generators[-i-1].bid
                self.Fixed_single_cont_Total_expense_sum += Fixed_single_cont_payment_to_generator



    def Fixed_single_cont_pay_to_agents(self):
        Fixed_single_cont_sum_all_bids = sum([sum(filter(None,x)) for x in self.Fixed_single_cont_bids_dict.values()])
        print('Fixed single cont: The sum all of the bids is ',Fixed_single_cont_sum_all_bids, '$')
        Fixed_single_cont_sum_all_q = sum([sum(filter(None, x)) for x in self.Fixed_single_cont_q_dict.values()])
        print('Fixed single cont: The sum all of the relevant q is ', Fixed_single_cont_sum_all_q, 'KWh')
        self.Fixed_single_cont_sum_of_bids_in_optimal_set = 0

        #for id in self.optimal_set_after:

        for num in self.Fixed_single_cont_optimal_set_after:
            for key, value in self.Fixed_single_cont_bids_dict.items():
                if key == num:
                    print(value)
                    self.Fixed_single_cont_sum_of_bids_in_optimal_set += value[0]
        print('Fixed single cont- The sum of bids in optimal set is ', self.Fixed_single_cont_sum_of_bids_in_optimal_set, '$')
        self.Fixed_single_cont_Total_expense = []
        Fixed_single_cont_q_in_optimal_set = []
        for num in self.Fixed_single_cont_optimal_set_after:
            Fixed_single_cont_q_in_optimal_set.append(self.agents[num].q)
        self.Fixed_single_cont_Total_q_in_optimal_set = sum(Fixed_single_cont_q_in_optimal_set)
        print('Fixed single cont- The sum of q in optimal set is: ', self.Fixed_single_cont_Total_q_in_optimal_set, 'KWh')
        for i in self.Fixed_single_cont_optimal_set_after:
            Fixed_single_cont_r = (Fixed_single_cont_sum_all_bids - self.agents[i].Fixed_single_cont_bids[0]) - (self.Fixed_single_cont_sum_of_bids_in_optimal_set - self.agents[i].Fixed_single_cont_bids[0])
            self.Fixed_single_cont_Total_expense.append(Fixed_single_cont_r)
        self.Fixed_single_cont_Total_expense_sum = int(sum(self.Fixed_single_cont_Total_expense)) - self.Fixed_single_cont_sum_of_bids_in_optimal_set
        #print('Total payment of the Grid is ', self.Total_expense_sum, '$')

    def Fixed_single_cont_reliability(self):
        self.Fixed_single_cont_reliability_agents_q = []
        #self.Fixed_single_cont_reliability_agents_q.append(self.Fixed_single_cont_Use_reserve_q)
        for id in self.Fixed_single_cont_optimal_set_after:
            if id >= 0:
                Fixed_single_cont_random_number = rd.uniform(0, 1)
                if self.agents[id].p >= Fixed_single_cont_random_number:
                    self.Fixed_single_cont_reliability_agents_q.append(self.agents[id].Fixed_single_cont_l_of_selected_cont)
                #agent pays the contrect f
                else:
                    self.Fixed_single_cont_Total_expense_sum -= self.agents[id].Fixed_single_cont_f_of_selected_cont
            else:
                self.Fixed_single_cont_reliability_agents_q.append(self.generators[-id-1].l)
        #print('The reliable agents reduce :', self.reliability_agents_q)
        self.Fixed_single_cont_reliability_sum_q = sum(self.Fixed_single_cont_reliability_agents_q)
        print('Fixed single cont- The reliabel sum of q in optimal set is: ', self.Fixed_single_cont_reliability_sum_q, 'KWh')
        #print('The sum of reliability agents is: ', self.Fixed_single_cont_reliability_sum_q)
        if self.Fixed_single_cont_reliability_sum_q >= self.M:
            print('Fixed single cont- The grid met the demand')
        else:
            print('Fixed single cont- The grid doesn\'t met the demand')
































