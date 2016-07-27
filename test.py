#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-07-18 16:32:40
# @Author  : jiong (447991103@qq.com)
# @Version : $Id$

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
from lxml import etree
# the search engine is divided into 3 modules:web crawl,build and use of
# index,page rank

#----------------------------web_crawl--------------------------------


def get_page(url):
    try:
        import urllib
        return urllib.urlopen(url).read()
    except:
        return ""


def get_next_target(content):
    start_link = content.find('<a href=')
    if start_link == -1:
        return None, 0
    # 将地址url 进行 划分
    start_quote = content.find('"', start_link)
    end_quote = content.find('"', start_quote + 1)
    url = content[start_quote + 1:end_quote]
    return url, end_quote


def get_all_links(content):
    links = []
    while True:
        url, endpos = get_next_target(content)

        content = content[endpos:]
        if url:
            if url_valid(url):
                links.append(url)
        else:
            break
    return links


def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)

# https://book.douban.com/subject/26698660/


def url_valid(url):
    """
    所爬取到的url需要符合特定的规则
    """
    import re
    res1 = re.match(r'^https://book.douban.com/$', url)
    res2 = re.match(r'^https://book.douban.com/subject/[0-9]{8}/$', url)

    if res1 or res2:
        # print 'url_valid:', url
        return True
    else:
        return False


def crawl_web(seed):  # returns index, graph of inlinks
    to_crawl = [seed]  # 待抓取队列
    crawled = []  # 已抓取队列
    graph = {}  # {<url>, [list of pages it links to],...}
    index = {}
    while to_crawl:
        # print 'to_crawl', to_crawl
        url = to_crawl.pop(0)

        # 做的去重
        if url not in crawled:
            content = get_page(url)
            # print '1'
            add_page_to_index(index, url, content)
            outlinks = get_all_links(content)
            graph[url] = outlinks

            # 下面这句，如果连接地址不在之前原来的地址池中，就继续入队进行爬取
            # 这样有一个问题就是，从豆瓣读书主页进行爬取的话，引出地址实在太多
            # 而且大部分地址都是没有什么用的，对于我们要爬取图书信息来说

            # 链接太多，太占内存

            # 解决方案 想了两种， 一是 爬取的时候进行深度的限制；
            # 二是 直接对抓取队列长度进行限制，达到一定长度入队

            union(to_crawl, outlinks)

            crawled.append(url)

            # 限制爬虫的爬取数量
            if len(crawled) > 10:
                break
    return index, graph

#--------------------------------html_parser-----------------------------------
#  拿出来放在另外一个模块里了

# def html_parser(url, content):

#     info = {}
#     if re.match(r'^https://book.douban.com/subject/[0-9]{8}/$', url):
#         selector = etree.HTML(content)
#         info['作者'] = selector.xpath('//*[@id="info"]/span[1]/a/text()')
#         print '作者',info['作者']
#         info['出版社'] = selector.xpath('//*[@id="info"]/span[2]/text()')
#         print info['出版社']
#         info['副标题'] = selector.xpath('//*[@id="info"]/br[2]/text()')
#         print info['副标题']
#         return info

#     else:
#         return None


#--------------------------------build_index-----------------------------------
def add_page_to_index(index, url, content):
    """
    这边呢，网页源码不经过修改，直接这样划分的，索引值太多，其中大部分也是没有用的。

    对于抓取特定书籍这样的情况，关键词最好直接自己定义（有待完善）。
    """
    # add_to_index(index, 'book', url)

    from html_parser import keywords, book_info
    # words = content.split()
    info = {}
    info = book_info(content)
    keyword = keywords(content)
    # print 'info', info

    for word in keyword:
        url_book_info = {url: info}
        add_to_index(index, word, url_book_info)
    # else:
    #     pass


def add_to_index(index, keyword, url_book_info):
    if keyword in index:
        index[keyword].append(url_book_info)
    else:
        index[keyword] = [url_book_info]


def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None


#---------------------------------page_rank---------------------------------

def compute_ranks(graph):
    """
    给每个url一个rank分值
    初始每个url分值一样，若它还在其余url的outlink中出现，
    则它的分值增加（增加值与所出现在的url本身数值有关）。

    num_loops 因为一开始给url赋值的时候，只有部分url的rank分值在改变，
    所以循环多次，将分数
    """
    d = 0.8  # damping factor
    num_loops = 10

    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages

    for i in range(0, num_loops):
        new_ranks = {}
        for page in graph:
            new_rank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    new_rank = new_rank + d * (ranks[node] / len(graph[node]))
            new_ranks[page] = new_rank
        ranks = new_ranks
    return ranks

#  可以直接按照ranks的 value值进行排序


def quick_sort(url_lst, ranks):
    url_sorted_worse = []
    url_sorted_better = []
    if len(url_lst) <= 1:
        return url_lst
    pivot = url_lst[0]
    for url in url_lst[1:]:
        if ranks[url] <= ranks[pivot]:
            url_sorted_worse.append(url)
        else:
            url_sorted_better.append(url)
    return quick_sort(url_sorted_better, ranks) + [pivot] + quick_sort(url_sorted_worse, ranks)


def ordered_search(index, ranks, keyword):
    if keyword in index:
        all_urls = []
        for each in index[keyword]:
            all_urls.extend(each.keys())
        # all_urls = index[keyword]
    else:
        return None
    return quick_sort(all_urls, ranks)


#---------------------------------test-----------------------------------



def search(search_term):

    # print 'ordered_search', ordered_search(index, ranks, u'二手')
    # print index[u'二手']
    # for each in index[u'二手']:

    #     for url in each:
    #         print url
    #         for a, b in each[url].items():
    #             print a,
    #             for info in b:
    #                 print info.encode('utf-8').decode('utf-8'),
    #             print
    #     print '----------I am fen ge xian----------'

	# search_term = raw_input('please input search words:')
	# search_term = u'二手 or 推荐'
	search_term = search_term.split(' ')
	if 'or' in search_term:
	    search_term.remove('or')

	for each in search_term:
	    print 'ordered_search', ordered_search(index, ranks, each)
	    for each in index[each]:

	        for url in each:
	            print url
	            for a, b in each[url].items():
	                print a,
	                for info in b:

	                    print info.encode('utf-8').decode('utf-8'),
	                print
	        print '----------I am fen ge xian----------'




if __name__ == '__main__':
    index, graph = crawl_web('https://book.douban.com/')
    # print index
    # print len(index.keys())
    print 'index.keys()'
    for each in index.keys():
    	print type(each)
        print each#.encode('gbk').decode('gbk')
    print 'graph.keys()',graph.keys()

    ranks = compute_ranks(graph)

    print u'-----单个关键词测试-----'
    search(u'黄磊')
    print u'-----or逻辑搜索测试-----'
    search(u'二手 or 推荐')