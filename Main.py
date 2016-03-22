#coding=utf-8
#Zhihu_spider Version 1.1 By Bluemit

from bs4 import BeautifulSoup
import urlparse
import urllib2
import re


class UrlManager(object):
    def __init__(self):
        self.new_urls = set()
        self.old_urls = set()

    def add_new_url(self, url):
        if url is None:
            return
        if url not in self.new_urls and url not in self.old_urls:
            # print self.old_urls
            self.new_urls.add(url)

    def add_new_urls(self, urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_new_url(url)

    def has_new_url(self):
        return len(self.new_urls) != 0

    def get_new_url(self):
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url


class Downloader(object):
    def download(self, url):
        if url is None:
            return None
        response = urllib2.urlopen(url)
        
        if response.getcode() != 200:
            return None
        # print response.read()
        return response.read()


class Zhihu_Parser(object):
# 知乎网页解析器
    def _get_new_urls(self, page_url, soup):
        new_urls = []
        #新的问题 <a class="question_link" href="/question/39053063">...</a>
        for link in soup.find_all('a',class_="question_link",href=re.compile(r"/question/\d")):
            # print 0
            # print page_url
            new_url = (link.get('href'))
            # print new_url
            new_full_url = urlparse.urljoin('https://www.zhihu.com', new_url)
            # print new_full_url
            new_urls.append(new_full_url)

        return new_urls

    def _get_new_data(self, page_url, soup):
        res_data = {}
        res_data['url'] = page_url
        title = soup.find('h2', class_='zm-item-title')
        # print title
        # print "title"
        res_data['title'] = title.get_text()
        # print title.get_text()
        # print 'title'
        #赞同数代码：<span class="count">273</span>
        #答案号代码：<a class="zg-anchor-hidden" name="answer-30358716"></a>
        answers = soup.find_all('div', class_="zm-item-vote-info")
        # print answers
        # print 'answers'
        # answer_urls=soup.find_all('a', class_="count")
        maxcount=0
        res_data['counts'] = 0
        if answers is None:
            res_data['counts'] = 0
        for answer in answers:
            # print answer['data-votecount']
            # en=answer.get_text().encode("utf-8")
            en = eval(answer['data-votecount'].encode("utf-8"))
            print en
            if en>maxcount:
                maxcount=en
                res_data['counts']=maxcount
            # if en.find('K')!=-1:
            #     res_data['counts'] = en
            #     res_data['status'] = 0
            #     print "to1"
            #     break
            # if eval(en)<100:
            #     print 777
            #     print answer.get_text()
            #     continue
            # else:
            #     # print 888
            #     if(eval(en)>maxcount):
            #         maxcount=eval(en)
            #         res_data['counts'] = maxcount
            #         res_data['status'] = 1
        if(maxcount>=200000):
            fout=open('result.html','a')
            fout.write("<a href='%s'>%s ( %s 赞同)</a><br />" % (res_data["url"].encode("utf-8"), res_data['title'].encode("utf-8"),res_data["counts"]))
            fout.close()
        return res_data

    def parse(self, page_url, html_cont):
        if page_url is None or html_cont is None:
            return
        soup = BeautifulSoup(html_cont, 'html.parser',from_encoding='utf-8')
        new_urls = self._get_new_urls(page_url, soup)
        # print 22222
        new_data = self._get_new_data(page_url, soup)
        # print 33333
        return new_urls, new_data



class Outputer(object):
    def __init__(self):
        self.datas=[]


    def collect_data(self,data):
        if data is None:
            return
        self.datas.append(data)


    def output_html(self):
        fout=open('result.html','a')
        fout.write("</p>")
        fout.write('<br /><br /><p style="text-align:center">Power By Bluemit</p>')
        fout.write("</body>")
        fout.write("</html>")


class SpiderMain():
    def craw(self,root_url,times): 
        fout=open('result.html','w')
        fout.write("<!DOCTYPE html>")
        fout.write("<html>")
        fout.write("<head>")
        fout.write('<meta charset="utf-8"></meta>')
        fout.write("<title>用爬虫爬取知乎赞同数超过20K的答案合集</title>")
        fout.write("</head>")
        fout.write("<body>")
        fout.write('<h2 style="text-align:center" >用爬虫爬取知乎赞同数超过20K的答案合集(不定期更新)</h2>')
        fout.write('<h3 style="text-align:center"> 2016-3-23</h3>')
        fout.write('<p style="align=center">')
        fout.close()
        count=1
        UrlManager.add_new_url(root_url)
        while UrlManager.has_new_url():
            try:
                new_url=UrlManager.get_new_url()
                print "\n%d: crawling %s" %(count,new_url)
                html_cont=Downloader.download(new_url)
                print new_url
                # print 12345
                new_urls,new_data=Parser.parse(new_url,html_cont)
                # print 111
                UrlManager.add_new_urls(new_urls)
                Outputer.collect_data(new_data)
                if count==times:
                    break
                count=count+1
            except:
                print "crawl failed" 
        Outputer.output_html()


if __name__=="__main__":
    print "Welcome to Zhihu spider"

    UrlManager = UrlManager()
    Downloader = Downloader()
    Parser = Zhihu_Parser()
    Outputer = Outputer()
    root = raw_input("Enter First Url : https://www.zhihu.com/question/ ")
    root_url = "https://www.zhihu.com/question/%s" %(root)
        

    times = input("Craw Times : ")
    SpiderMain = SpiderMain()
    root_url=unicode(root_url,'utf-8')
    SpiderMain.craw(root_url,times)
    print "\nEverything is done. Result is in result.html ."