import requests, os, re, json
from multiprocessing import Pool

class Lian():
	
	def __init__(self):
		self.process = 4 #进程数设置
		self.headers = {'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36'}
		self.re_index_1 = re.compile('<div id="dh.*?>(.*?)</div></span>',re.S)
		self.re_index_2 = re.compile('a[\s=":;a-z]*?href="([/a-z0-9]*?)".tar.*?>(.*?)<',re.S)
		try:
			with open('video.json') as f:
				self.video_number = json.load(f)
		except:
			self.video_number = {}
			f = open('video.json', 'w')
			f.close()
		
	def get_index(self):
		try:
			r = requests.get("http://v7.22n.im/", headers = self.headers)
		except:
			print("无法访问恋恋影视，请检查网络！")
		if r.status_code == 200:
			tmp = re.search(self.re_index_1, r.text).group()
			index = re.findall(self.re_index_2, tmp)
			index.remove(('/vip', '开通VIP会员'))
			return index
		else:
			print("发生错误，错误原因：" + res.status_code)
			return None
			
	def get_video_number(self,link):
		page_link = []
		url = "http://v7.22n.im" + link
		try:
			r = requests.get(url, headers = self.headers)
		except:
			print("无法访问恋恋影视，请检查网络！")
		try:
			last = re.search('id="hm".*?href="' + link + '(.*?)"', r.text, re.S)
			return int(last.group(1))
		except:
			return 0
	
	def get_download_link(self, index, number):
		t = index + str(number)
		url = 'http://h.syasn.com/?n=' + t + '&p=222222222'
		headers = self.headers
		headers['Referer'] = 'http://v7.22n.im/' + t
		try:
			r = requests.get(url, headers = headers)
		except:
			print("获取下载链接失败，请检查网络！")
		p = {}
		for item in r.text[:-1].split(","):
			n1,n2 = item.split("=")
			p[n1] = n2.replace("'","")			
		d_link = "https://k.syasn.com/{index}/{t}.mp4?k1={k1}&k2=ms&k3={k3}&k4={k4}&k5={k5}&k7=8.1.0&g=0".format(index = index, t = t, k1 = p['mip'], k3 = p['mik'], k4 = p['min'], k5 = p['mis'])
		url = 'http://v7.22n.im/' + t
		try:
			r = requests.get(url, headers = self.headers)
		except:
			print("获取下载链接失败，请检查网络！")
		try:
			name = re.search('<span id="pt1">(.*?)</span>', r.text, re.S).group(1)
			return d_link,name
		except:
			return str(number)
	
	def download_video(self, url, filename):
		r = requests.get(url, stream=True)
		chunk_size=1048576
		try:
			content_size = int(r.headers['content-length'])
			chunk_size = int(content_size/5+1)
			print("开始下载" + os.path.split(filename)[1] + "文件大小"+ round(content_size/1048576,2) + "MB")
		except:
			print("开始下载" + os.path.split(filename)[1])
		with open(filename, "wb") as f:
			i=1
			for chunk in r.iter_content(chunk_size=chunk_size):
				if chunk:
					print(os.path.split(filename)[1] + "已下载" + str(i*20) + "%")
					f.write(chunk)
					i += 1
		print(os.path.split(filename)[1] + "下载完成")
		
	def downloads(self, n, index, dir_name):
		url,name = self.get_download_link(index[1:], n)
		name = name + '.mp4'
		filename = os.path.join(dir_name, name)
		self.download_video(url, filename)
		if n >= self.video_number[dir_name]:
			self.video_number[dir_name] = n	
			with open('video.json', 'w') as f:
				json.dump(self.video_number, f)				

v=Lian()

if __name__=='__main__':
	index = v.get_index()
	for i in index:
		number = v.get_video_number(i[0])
		c_number = v.video_number.get(i[1],1)
		if number > c_number:
			v.video_number[i[1]] = c_number
			if not os.path.exists(i[1]):
				os.mkdir(i[1])
			p = Pool(v.process)
			for n in range(c_number,number+1):
				p.apply_async(v.downloads, args=(n,i[0],i[1]))
			print("开始下载" + i[1] + "目录")
			p.close()
			p.join()
			print("下载" + i[1] + "目录完成")
