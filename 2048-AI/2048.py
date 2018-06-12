#! python3
# 不断发送方向键给2048游戏网站
# 模拟每一步后计算优劣性决定
# 结果记录到2048.txt

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, random, re
import model  #游戏建模函数

browser = webdriver.Firefox()
browser.maximize_window()
browser.get('http://gabrielecirulli.github.io/2048/')

bodyElem = browser.find_element_by_tag_name('body')

# 记入成绩的txt文件
writeInFile = '2048.txt'

# 规定方向键顺序
dirKey = ['UP', 'RIGHT', 'DOWN', 'LEFT']

# 判断权值后发送方向键
def sendDirKey():
	# 判断最好方向
	bestDir = model.scoringSimu()
	# 发送方向键
	if bestDir == 0:
		bodyElem.send_keys(Keys.UP)
	elif bestDir == 1:
		bodyElem.send_keys(Keys.RIGHT)
	elif bestDir == 2:
		bodyElem.send_keys(Keys.DOWN)
	elif bestDir == 3:
		bodyElem.send_keys(Keys.LEFT)

# 循环发送方向键
for i in range(10000):
	# 对当前画面建模
	# 返回false时，说明程序运行过快，tile元素已不在原DOM中，搜索不到，所以跳过此次循环
	if model.getModel(browser) == False:
		continue
	# 发送方向键
	sendDirKey()
	time.sleep(0.02)
	# 检测游戏是否失败
	try:
		if browser.find_element_by_class_name('game-over'):
			break
	except:
		None
	# 检测游戏是否胜利
	try:
		if browser.find_element_by_class_name('game-won'):
			break
	except:
		None

# 游戏结束，获取分数
score = browser.find_element_by_class_name('score-container').text
score = score.split('\n')[0]
# 获取方块最大数字
tiles = browser.find_elements_by_class_name('tile')
achie = 2
for tile in tiles:
	if achie < int(tile.text):
		achie = int(tile.text)

# 创建txt文件
addFile = open(writeInFile, 'a')
# 查找写入文件时的序数
addFile = open(writeInFile, 'r')
numRegex = re.compile(r'<([\d]+)>')
mo = numRegex.findall(addFile.read())
nextFileNum = 0
for i in mo:
	if int(i) > nextFileNum:
		nextFileNum = int(i)
nextFileNum += 1

# 将成绩写入txt
addFile = open(writeInFile, 'a')
addFile.write('\n<%d>' %nextFileNum)
addFile.write('\nYour score: %s' %score)
addFile.write('\nYour achievement: %d\n' %achie)
addFile.close()

# 关闭浏览器
browser.quit()