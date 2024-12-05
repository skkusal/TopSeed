import numpy as np
import random
from collections import defaultdict
from sklearn.cluster import KMeans
from scipy.stats import truncnorm

def update(n_features, weightdata, policyInfo, prob_p, n_section):
    kmeans = KMeans(n_clusters=2, random_state=0)

    branchFreq = defaultdict(int)

    for each in weightdata:
        for eachCoveredSet in each[1]:
            branchFreq[eachCoveredSet] += 1

    data = [[] for _ in range(n_features)]
    scores = []

    for each in weightdata:
        score = 0.0
        for eachCoveredSet in each[1]:
            score += 1 / branchFreq[eachCoveredSet]
        
        for j in range(n_features):
            data[j].append(each[0][j])
        scores.append(score)

    dataByFeature = [[] for _ in range(n_features)]
    dataByFeature2 = [[] for _ in range(n_features)]
    
    new_weight = [random.uniform(-1, 1) for _ in range(n_features)]
    prob_w_info = [[[-1, -1] for _ in range(n_section)] for _ in range(n_features)]
    
    prob_w_section = [[0.0 for _ in range(n_section)] for _ in range(n_features)]

    for i in range(n_features):
        WData = data[i]

        for j in range(len(WData)):
            dataByFeature[i].append([WData[j], scores[j]])
            dataByFeature2[i].append([0, scores[j]])

        X = np.array(dataByFeature2[i])
        Y = np.array(dataByFeature[i])
        kmeans.fit(X)

        labels = kmeans.labels_ 

        firstData = Y[labels == 0]
        secondData = Y[labels == 1]

        maxFirData = max(firstData, key=lambda x: x[1])
        maxSecData = max(secondData, key=lambda x: x[1])

        if maxFirData[1] < maxSecData[1]:
            filteredTopData = secondData
            filteredBotData = firstData
        else:
            filteredTopData = firstData
            filteredBotData = secondData

        topMean, _ = np.mean(filteredTopData, axis = 0)
        topStd, _ = np.std(filteredTopData, axis = 0)

        botMean, _ = np.mean(filteredBotData, axis = 0)
        botStd, _ = np.std(filteredBotData, axis = 0)

        if np.abs(topMean - botMean) + np.abs(topStd - botStd) > 0.1:
            dataSection = [[] for _ in range(n_section)]
            scoreSection = [[] for _ in range(n_section)]

            for k in range(len(filteredTopData)):
                eachWData = filteredTopData[k][0]
                eachScore = filteredTopData[k][1]

                for l in range(n_section):
                    if n_section == 10:
                        compare_value = -0.8 + 0.2 * l
                    elif n_section == 20:
                        compare_value = -0.9 + 0.1 * l
                    elif n_section == 1:
                        compare_value = 1.0
                    else:
                        # U HAVE TO IMPLEMENT BASED ON THE VALUE
                        pass 
                        
                    if eachWData <= compare_value:
                        dataSection[l].append(eachWData)
                        scoreSection[l].append(eachScore)
                        break

            sumCriteria = 0.0
            for l in range(n_section):
                if len(scoreSection[l]) == 0 or np.sum(scoreSection[l]) == 0:
                    prob_w_section[i][l] = 0.0
                else:
                    prob_w_info[i][l][0] = np.mean(dataSection[l])
                    prob_w_info[i][l][1] = np.std(dataSection[l]) if np.std(dataSection[l]) != 0.0 else 1.0

                    prob_w_section[i][l] = round(np.mean(scoreSection[l]), 1)
                    sumCriteria += prob_w_section[i][l]
            
            if sumCriteria != 0.0:
                for l in range(n_section):
                    prob_w_section[i][l] /= sumCriteria
            
            component = np.random.choice(n_section, p=prob_w_section[i])
            loc_ = prob_w_info[i][component][0]
            scale_ = prob_w_info[i][component][1]

            a_ = (-1.0 - loc_) / scale_
            b_ = (1.0 - loc_) / scale_

            sample = truncnorm.rvs(a=a_, b=b_, loc=loc_, scale=scale_)
            new_weight[i] = sample
        
        policyCov = list(policyInfo.values())
        
        if all(len(v) != 0 for v in policyCov):
            newpickCov = []
            newpickCovFreq = defaultdict(int)
            for j in range(len(policyCov)):
                policySet = policyCov[j]

                for each in policySet:
                    newpickCovFreq[each] += 1
            
            for j in range(len(policyCov)):
                policySet = policyCov[j]
                score = 0.0
                for each in policySet:
                    score += 1 / newpickCovFreq[each]

                newpickCov.append(score)
                    
            sumCov = sum(newpickCov)
            for j in range(len(prob_p)):
                prob_p[j] = newpickCov[j] / sumCov

    return new_weight, prob_p, prob_w_info, prob_w_section