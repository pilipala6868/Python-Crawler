#! python3
# 爬取alpha.wallhaven.cc的最新壁纸

import requests, os, bs4
import shelve
import threading, time
from queue import Queue

url = 'https://alpha.wallhaven.cc/latest'
threadSum = 10  # 线程总数
dirName = r'C:\Users\52714\Desktop\每日壁纸'  # 目录名称
os.makedirs(dirName, exist_ok=True)

# shelve获取上一次记录的最后下载的几张图片序数
shelfFile = shelve.open('myData')
if not 'alpha-wallhaven' in shelfFile.keys():  # 如果事先不存在该记录
	res = requests.get(url)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	picUrl = soup.select('ul li a.preview')[10:13]  # 第11、12、13张设为上次已经下载
	lastPicNum = [int(u.get('href').split('/')[-1]) for u in picUrl]
else:
	lastPicNum = shelfFile['alpha-wallhaven']
shelfFile.close()

# 搜索后获取图片链接
picUrls = []
picNames = []
for i in range(10000):
	# 循环太多页还找不到上次下载的最后一张图，有点奇怪，结束...
	if i >= 50:
		print('\nLast picNum missing...')
		os._exit(0)

	# 获取该页链接
	print('Getting page %d...' %(i+1))
	res = requests.get(url+'?page='+str(i+1))
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	picUrl = soup.select('ul li a.preview')

	# 检查是否是新的链接
	picUrlNum = [int(u.get('href').split('/')[-1]) for u in picUrl]
	lastIndex = len(picUrlNum)  # 保存该页图片应该下载的最后一张的位置
	for j in range(len(picUrlNum)):
		if picUrlNum[j] in lastPicNum:
			lastIndex = j
			break
	if lastIndex != len(picUrlNum):
		picUrls.extend(picUrl[:lastIndex])
		picNames.extend(picUrlNum[:lastIndex])
		break
	else:
		picUrls.extend(picUrl)
		picNames.extend(picUrlNum)

picSum = len(picUrls)  # 图片总数
print('\nFind %d pictures.\n' %picSum)


downloadSum = 0  # 下载成功的图片数
downloadFail = []  # 下载失败的图片序号
# 下载一张图片 (图片序数)
def downloadPic(pNum, threadID):
	# 打开图片链接
	singlePicUrl = picUrls[pNum].get('href')
	res = requests.get(singlePicUrl)
	res.raise_for_status()

	# 获取打开文件链接
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	imgUrl = soup.select('#wallpaper')[0].get('src')
	res = requests.get('http:'+imgUrl, timeout=10)
	res.raise_for_status()

	# 拼接文件名
	today = time.strftime("%Y-%m-%d", time.localtime())
	fileName = '%s %d.%s' %(today, picNames[pNum], imgUrl.split('.')[-1])

	# 下载图片
	with open(os.path.join(dirName, fileName), 'wb') as f:
		for chunk in res.iter_content(100000):
			f.write(chunk)
	print('Thread %d:\t' %threadID, end='')
	print('Download No.%d: %s' %(pNum+1, picNames[pNum]))

	global downloadSum
	downloadSum += 1


# 线程模块
class MyThread(threading.Thread):
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
	def run(self):
		print('Strating Thread %d' %self.threadID)
		# 下载出队图片
		while not q.empty():
			urlNum = q.get()
			try:
				downloadPic(urlNum, self.threadID)
			except Exception as e:
				print('Thread %d:\tTry to request again #1' %(self.threadID))
				# 请求超时，再试几次
				requestOK = False  # 标记
				exceptionMs = str(e)  # 先保存错误信息
				for i in range(4):
					try:
						downloadPic(urlNum, self.threadID)
						requestOK = True
						break
					except Exception as e:
						print('Thread %d:\tTry to request again #%d' %(self.threadID, (i+2)))
				# 请求多次还是不成功
				if not requestOK:
					downloadFail.append(picNames[urlNum])
					print('Thread %d:\t%s' %(self.threadID, exceptionMs))
		# 线程结束
		print('Exiting Thread %d' %self.threadID)


# 链接序号队列
q = Queue()
for i in range(picSum):
	q.put(i)

# 开始计时
stratTime = time.time()

# 创建线程
threads = []
for i in range(threadSum):
	thread = MyThread(i+1)
	threads.append(thread)
	# 开始进程
	thread.start()

# 等待所有进程完成
for t in threads:
	t.join()

# 结束计时
endTime = time.time()


# shelve保存前几张下载的图片序数
shelfFile = shelve.open('myData')
if len(picNames) > 3:  # 新图片超过3张才更新
	shelfFile['alpha-wallhaven'] = picNames[0:3]
shelfFile.close()


print('\nDone.')
print('Total time: %ds' %(endTime - stratTime))
print('Download pictures sum: %d\t%d failed.' %(downloadSum, (picSum-downloadSum)))

if len(downloadFail) != 0:
	print('\nFail picture number:', end='')
	for f in downloadFail:
		print(' ' + str(f), end='')

# 任意输入字符才结束
input()