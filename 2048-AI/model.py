#! python3
# 2048游戏建模

import time, random, re, copy

# 游戏模型变量
model = [([0]*4) for i in range(4)]  #当前模型
modelSimu = [([0]*4) for i in range(4)]	 #用于模拟下一步

# 单调性：平滑性：空闲方块的权值比例（经过多次运行、对比得出）
weightProp = [15, 4, 4]

# 打印游戏模型
def printModel(model):
	for i in range(4):
		for j in range(4):
			if model[i][j] == 0:
				print('    * ', end='')
			else:
				print('%5d ' %model[i][j], end='')
		print('\n')
	print('\n')

# 建立当前游戏二维数组模型
def getModel(browser):
	# 原模型清零
	global model
	model = [([0]*4) for i in range(4)]
	# 获取游戏页面
	tiles = browser.find_elements_by_class_name('tile')
	for tile in tiles:
		try:
			# 程序有时运行过快，tile元素已不在原DOM中，搜索不到，会报错
			tileClass = tile.get_attribute('class').split(' ')
		except:
			return False
		# 获取位置、数值
		tilePosiX = int(tileClass[2][-3])
		tilePosiY = int(tileClass[2][-1])
		tileNum = int(tileClass[1].split('-')[1])
		# 赋值给model
		model[tilePosiY-1][tilePosiX-1] = tileNum

# 模拟下一步的格局
def simulation(dir):
	# 初始化预测模型
	global modelSimu
	modelSimu = copy.deepcopy(model)
	# 上移
	if dir == 'UP':
		for j in range(4):
			# 先把所有方块上移
			for i in range(0,3):
				if modelSimu[i][j] == 0:
					for k in range(i+1,4):
						# 遇到有数字，交换
						if modelSimu[k][j] != 0:
							modelSimu[i][j],modelSimu[k][j] = modelSimu[k][j],modelSimu[i][j]
							break
					if k == 4:
						break
			# 检测有无方块可合并
			for i in range(1,4):
				if modelSimu[i][j] == 0:
					break
				elif modelSimu[i][j] == modelSimu[i-1][j]:
					# 合并方块
					modelSimu[i-1][j] *= 2
					# 后面方块前移
					for k in range(i,3):
						modelSimu[k][j] = modelSimu[k+1][j]
					modelSimu[3][j] = 0
	# 右移
	elif dir == 'RIGHT':
		for i in range(4):
			# 先把所有方块下移
			for j in range(3,0,-1):
				if modelSimu[i][j] == 0:
					for k in range(j-1,-1,-1):
						# 遇到有数字，交换
						if modelSimu[i][k] != 0:
							modelSimu[i][j],modelSimu[i][k] = modelSimu[i][k],modelSimu[i][j]
							break
					if k == -1:
						break
			# 检测有无方块可合并
			for j in range(2,-1,-1):
				if modelSimu[i][j] == 0:
					break
				elif modelSimu[i][j] == modelSimu[i][j+1]:
					# 合并方块
					modelSimu[i][j+1] *= 2
					# 后面方块前移
					for k in range(j,0,-1):
						modelSimu[i][k] = modelSimu[i][k-1]
					modelSimu[i][0] = 0
	# 下移
	elif dir == 'DOWN':
		for j in range(4):
			# 先把所有方块下移
			for i in range(3,0,-1):
				if modelSimu[i][j] == 0:
					for k in range(i-1,-1,-1):
						# 遇到有数字，交换
						if modelSimu[k][j] != 0:
							modelSimu[i][j],modelSimu[k][j] = modelSimu[k][j],modelSimu[i][j]
							break
					if k == -1:
						break
			# 检测有无方块可合并
			for i in range(2,-1,-1):
				if modelSimu[i][j] == 0:
					break
				elif modelSimu[i][j] == modelSimu[i+1][j]:
					# 合并方块
					modelSimu[i+1][j] *= 2
					# 后面方块前移
					for k in range(i,0,-1):
						modelSimu[k][j] = modelSimu[k-1][j]
					modelSimu[0][j] = 0
	# 左移
	elif dir == 'LEFT':
		for i in range(4):
			# 先把所有方块左移
			for j in range(0,3):
				if modelSimu[i][j] == 0:
					for k in range(j+1,4):
						# 遇到有数字，交换
						if modelSimu[i][k] != 0:
							modelSimu[i][j],modelSimu[i][k] = modelSimu[i][k],modelSimu[i][j]
							break
					if k == 4:
						break
			# 检测有无方块可合并
			for j in range(1,4):
				if modelSimu[i][j] == 0:
					break
				elif modelSimu[i][j] == modelSimu[i][j-1]:
					# 合并方块
					modelSimu[i][j-1] *= 2
					# 后面方块前移
					for k in range(j,3):
						modelSimu[i][k] = modelSimu[i][k+1]
					modelSimu[i][3] = 0
	
# 单调性得分
def monotonicity():
	score = 100  #初始化分数
	subtract = score / (2*4*4)  #每次减去的基数
	# 求当前所有数字的平均数
	average = 0 
	for i in range(4):
		for j in range(4):
			average += modelSimu[i][j]
	average /= 16

	# 检测最高数字所在区域
	maxNum = {'num': 0, 'i': 0, 'j': 0}
	for i in range(4):
		for j in range(4):
			if modelSimu[i][j] > maxNum['num']:
				maxNum['num'] = modelSimu[i][j]
				maxNum['i'] = i
				maxNum['j'] = j

	# 左-右：递减
	if maxNum['j'] < 2:
		for i in range(4):
			for j in range(1,4):
				if modelSimu[i][j] > modelSimu[i][j-1]:
					score -= subtract * ((modelSimu[i][j]-modelSimu[i][j-1])/average)
	# 左-右：递增
	else:
		for i in range(4):
			for j in range(1,4):
				if modelSimu[i][j] < modelSimu[i][j-1]:
					score -= subtract * ((modelSimu[i][j-1]-modelSimu[i][j])/average)
	# 上-下：递减
	if maxNum['i'] < 2:
		for j in range(4):
			for i in range(1,4):
				if modelSimu[i][j] > modelSimu[i-1][j]:
					score -= subtract * ((modelSimu[i][j]-modelSimu[i-1][j])/average)
	# 上-下：递增
	else:
		for j in range(4):
			for i in range(1,4):
				if modelSimu[i][j] < modelSimu[i-1][j]:
					score -= subtract * ((modelSimu[i-1][j]-modelSimu[i][j])/average)
	return score
	
# 平滑性得分
def smoothness():
	score = 0  #初始化分数
	plus = 20  #每次加上的基数
	# 求当前所有数字的平均数
	average = 0 
	for i in range(4):
		for j in range(4):
			average += modelSimu[i][j]
	average /= 16

	# 横向扫描
	for i in range(4):
		for j in range(1,4):
			if modelSimu[i][j] == modelSimu[i][j-1]:
				score += plus * (modelSimu[i][j] / average)
	# 纵向扫描
	for j in range(4):
		for i in range(1,4):
			if modelSimu[i][j] == modelSimu[i-1][j]:
				score += plus * (modelSimu[i][j] / average)
	return score
	
# 空闲方块加分
def freeTiles():
	score = 0  #初始化分数
	plus = 10  #每次加上的基数
	# 遍历数组
	for j in range(4):
		for i in range(4):
			if modelSimu[i][j] == 0:
				score += plus
	return score

# 检测是否下一步就是2048
def get2048():
	score = 0  #初始化分数
	# 遍历数组
	for j in range(4):
		for i in range(4):
			if modelSimu[i][j] == 2048:
				score += 1000000
	return score

	
# 对所有结果总分评估
dirKey = ['UP', 'RIGHT', 'DOWN', 'LEFT']
def scoringSimu():
	scores = [0]*4
	for i in range(4):
		simulation(dirKey[i])
		# 该方向无法移动
		if model == modelSimu:
			scores[i] = 0
		else:
			scores[i] = monotonicity()*weightProp[0] + smoothness()*weightProp[1] + freeTiles()*weightProp[2] + get2048()
	return scores.index(max(scores))