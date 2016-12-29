#coding=utf-8
import scrapy
from bs4 import BeautifulSoup
import os
import re
import urlparse


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"

    def start_requests(self):
        self.new_urls = set()
        self.old_urls = set()
        self.count = 0
        self.times = 50000
        root_url = 'https://www.zhihu.com/question/54076872'
        self.old_urls.add(root_url)
        fout = open('result.html', 'w')
        fout.write("<!DOCTYPE html>")
        fout.write("<html>")
        fout.write("<head>")
        fout.write('<meta charset="utf-8"></meta>')
        fout.write("<title>知乎赞同数超过20K的答案合集</title>")
        fout.write("</head>")
        fout.write("<body>")
        fout.write('<h2 style="text-align:center" >知乎赞同数超过20K的答案合集</h2>')
        fout.write('<h3 style="text-align:center">Bluemit</h3>')
        fout.write('<p style="align=center">')
        fout.close()
        print "\n%d: crawling %s" % (self.count, root_url)
        yield scrapy.Request(url=root_url, callback=self.parse)

    def _get_new_data(self, page_url, soup):
        res_data = {}
        res_data['url'] = page_url
        title = soup.find('h2', class_='zm-item-title')
        res_data['title'] = title.get_text()
        # 赞同数代码：<span class="count">273</span>
        # 答案号代码：<a class="zg-anchor-hidden" name="answer-30358716"></a>
        answers = soup.find_all('div', class_="zm-item-vote-info")
        maxcount=0
        res_data['counts'] = 0
        if answers is None:
            res_data['counts'] = 0
        for answer in answers:
            en = eval(answer['data-votecount'].encode("utf-8"))
            if en > maxcount:
                maxcount = en
                res_data['counts'] = maxcount

        if(maxcount >= 20000):
            fout = open('result.html', 'a')
            fout.write("<a href='%s'>%s ( %s 赞同)</a><br />" % (res_data["url"].encode("utf-8"), res_data['title'].encode("utf-8"),res_data["counts"]))
            fout.close()
            fout = open('result.txt', 'a')
            fout.write(res_data["url"].encode("utf-8").strip()+'\t'+res_data['title'].encode("utf-8").strip()+'\t'+str(res_data["counts"]))
            fout.write('\n')
            fout.close()
        return res_data

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        page_url = response.url
        new_urls = []
        # 新的问题格式 <a class="question_link" href="/question/39053063">...</a>
        for link in soup.find_all('a',class_="question_link",href=re.compile(r"/question/\d")):
            new_url = (link.get('href'))
            new_full_url = urlparse.urljoin('https://www.zhihu.com', new_url)
            new_urls.append(new_full_url)
        self._get_new_data(page_url, soup)
        for item in new_urls:
            if item in self.old_urls:
                continue
            self.old_urls.add(item)
            if self.count == self.times:
                break
            self.count += 1
            print "\n%d: crawling %s" % (self.count, item.strip())
            yield scrapy.Request(url=item, callback=self.parse)
