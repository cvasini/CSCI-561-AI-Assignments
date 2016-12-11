from collections import deque
import heapq
import os.path
import filecmp
for nthInput in range(1000, 1100):
    f = open("BFS/Input/CROSSFIRE"+str(nthInput)+".txt")
    lines = f.readlines()
    algo = "BFS"
    startState = lines[1].rstrip('\n')
    goalState = lines[2].rstrip('\n')
    noOfLive = int(lines[3].rstrip('\n'))
    f.close()
    #create states
    states = set()
    sundayLines = {}
    with open("BFS/Input/CROSSFIRE"+str(nthInput)+".txt") as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            if i >= 4 and i<= (3 + noOfLive):
                list1 = line.split(" ")
                list1.pop()
                states = states.union(list1)
            if algo == "A*":
                if i == (4 + noOfLive):
                    noOfSLines = int(line)
                elif i >= (4 + noOfLive) and i <= (noOfSLines + noOfLive+4):
                    list2 = line.split(" ")
                    sundayLines[list2[0]] = []
                    sundayLines[list2[0]].append(int(list2[1]))
    states = sorted(states)
    routes = {}
    for j in states:
        routes[j] = []
    #create routes
    with open("BFS/Input/CROSSFIRE"+str(nthInput)+".txt") as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            if i >= 4 and i<= (3 + noOfLive):
                list1 = line.split(" ")
                routes[list1[0]].append([list1[1], int(list1[2])])
    visited = []
    #create output file
    if os.path.isfile("BFSOutput/CROSSFIRE"+str(nthInput)+".txt"):
        wf = open("BFSOutput/CROSSFIRE"+str(nthInput)+".txt", 'w')
        wf.truncate()
    else:
        wf = open("BFSOutput/CROSSFIRE"+str(nthInput)+".txt", 'w')
    def findSecondPriority(costs, cost):
        n = 0
        for c in costs:
            if cost == c:
                n+=1
        return n
    def findNodeForPQNode(value):
        for node in visited:
            if node[2]["stateName"] == value:
                return node[2]
    def findWeightOfNextNodeForPQNode(value, valueParent):
        for node in visited:
            if node[2]["stateName"] == value and node[2]["parent"] == valueParent:
                return node[2]["cost"]
    def findNode(value):
        for node in visited:
            if node["stateName"] == value:
                return node
    def findWeightOfNextNode(value, valueParent):
        for node in visited:
            if node["stateName"] == value and node["parent"] == valueParent:
                return node["cost"]
    def createNode(stateName, cost, parent):
        node = {}
        node["stateName"] = stateName
        node["parent"] = parent
        node["children"] = routes[stateName]
        node["cost"] = cost
        if algo == "A*":
            node["heuristic"] = sundayLines[stateName][0]
        return node
    def compareObjects(node, queue1):
        present = False
        nodeOccuring = []
        for n in queue1:
            if node["stateName"] == n["stateName"]:
                present = True
                nodeOccuring = n
                break
        return {"nodeOccuring" : nodeOccuring, "present" :present}
    def comparePQObjects(node, queue1):
        present = False
        nodeOccuring = []
        for n in queue1:
            if node["stateName"] == n[2]["stateName"]:
                present = True
                nodeOccuring = n
                break
        return {"nodeOccuring" : nodeOccuring, "present" :present}
    def bfsOrDfs():
        if startState == goalState:
            return True
        queue1 = deque()
        queue1.append(createNode(startState, 0, ""))
        while queue1:
            node = queue1.popleft()
            visited.append(node)
            if node["stateName"] == goalState:
                return True
            routesToUse = node["children"]
            if algo == "DFS":
                routesToUse.reverse()
            for n in routesToUse:
                newNode = createNode(n[0], n[1], node["stateName"])
                if not compareObjects(newNode, visited)["present"] and not compareObjects(newNode, queue1)["present"]:
                    if algo == 'BFS':
                        queue1.append(newNode)
                    elif algo == 'DFS':
                        queue1.appendleft(newNode)
    def updatePQParentAndCost(oldNode, newNode, parent, pQ, costs, newCost):
        copyPQ = []
        for n in pQ:
            if oldNode["stateName"] == n[2]["stateName"]:
                oldCost = n[0]
                if newCost < oldCost:
                    n[2]["cost"] = newNode["cost"]
                    n[2]["parent"] = parent["stateName"]
                    costs.append(newCost)
                    heapq.heappush(copyPQ, (newCost, findSecondPriority(costs, newCost), n[2]))
                else:
                    heapq.heappush(copyPQ, (n[0], n[1], n[2]))
            else:
                heapq.heappush(copyPQ, (n[0], n[1], n[2]))
        return copyPQ
    def findPathCost(currentNode, parentNode):
        cost = currentNode["cost"] + parentNode["cost"]
        while parentNode["stateName"] != startState:
            parentNode = findNodeForPQNode(parentNode["parent"])
            cost += parentNode["cost"]
        return cost
    def ucsOrA():
        if startState == goalState:
            return True
        priorityQueue = []
        costs = []
        costs.append(0)
        if algo == "UCS":
            heapq.heappush(priorityQueue, (0, 1, createNode(startState, 0, "")))
        else:
            heapq.heappush(priorityQueue, (sundayLines[startState][0], 1, createNode(startState, 0, "")))
        while priorityQueue[0]:
            node = heapq.heappop(priorityQueue)
            visited.append(node)
            if node[2]["stateName"] == goalState:
                return True
            routesToUse = node[2]["children"]
            for n in routesToUse:
                newNode = createNode(n[0], n[1], node[2]["stateName"])
                comparePQ = comparePQObjects(newNode, priorityQueue)
                compareVisited = comparePQObjects(newNode, visited)
                cost = findPathCost(newNode, node[2])
                if algo == "A*":
                    cost += newNode["heuristic"]
                if not compareVisited["present"] and not comparePQ["present"]:
                        costs.append(cost)
                        heapq.heappush(priorityQueue, (cost, findSecondPriority(costs, cost), newNode))
                elif not compareVisited["present"] and comparePQ["present"]:
                    priorityQueue = updatePQParentAndCost(comparePQ["nodeOccuring"][2], newNode, node[2], priorityQueue, costs, cost)
                elif compareVisited["present"] and not comparePQ["present"]:
                    if cost < compareVisited["nodeOccuring"][0]:
                        costs.append(cost)
                        visited.remove(compareVisited["nodeOccuring"])
                        heapq.heappush(priorityQueue, (cost, findSecondPriority(costs, cost), newNode))
    result = False
    if algo == "UCS" or algo == "A*":
        result = ucsOrA()
    elif algo == "BFS" or algo == "DFS":
        result = bfsOrDfs()
    if result:
            output = deque()
            output.append(goalState)
            value = {}
            value = goalState
            if algo == "BFS" or algo == "DFS":
                while value != startState:
                    value = findNode(value)["parent"]
                    output.appendleft(value)
                weight = 0
                for nodeName in output:
                    wf.write(nodeName +" "+ str(weight))
                    if output[len(output)-1] != nodeName:
                        wf.write("\n")
                    weight= weight + 1
                wf.close()
            elif algo == "UCS" or algo == "A*":
                weight = 0
                while value != startState:
                    value = findNodeForPQNode(value)["parent"]
                    output.appendleft(value)
                for n in range(len(output)):
                    wf.write(output[n] +" "+ str(weight))
                    if n+1 != len(output):
                        wf.write("\n")
                    if n+1 < len(output):
                        weight= findWeightOfNextNodeForPQNode(output[n+1], output[n]) + weight
                wf.close()
    w1 = open("BFSOutput/CROSSFIRE"+str(nthInput)+".txt")
    aa = []
    bb = []
    for n in w1:
        aa.append(n)
    w2 = open("BFS/Output/CROSSFIRE"+str(nthInput)+".txt")
    for n in w2:
        bb.append(n)
    for n in range(len(aa)):
        if aa[n] != bb[n]:
            print ("Test case " + str(nthInput) + " failed")
    if nthInput == 1099:
        print ("end")
