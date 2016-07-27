#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-07-19 15:05:51
# @Author  : jiong (447991103@qq.com)
# @Version : $Id$
"""

网页抽取模块，从其中抽取出keywords 和 book_info
book_info(content)
keywords(content)
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib
from lxml import etree


"""
从网页中获取图书信息book_info，字典的形式，value值是list形式
"""
def book_info(content):

	# content = urllib.urlopen(
	# 	'https://book.douban.com/subject/25960141/').read()
	sel = etree.HTML(content)
	# print content

	# 将无用信息去除，同时将图书信息转化为字典的形式
	res = sel.xpath('string(//*[@id="info"])').replace('\n',
													   '').replace(u'著', '').replace(u'/', '').split(' ')
	res1 = []
	for each in res:
		if each != '':
			res1.append(each)
	# print res1
	# print len(res1)
	book_info = {}
	for a in range(len(res1) - 1):
		if res1[a][-1] == ':':
			b = a + 1
			while res1[b][-1] != ':':

				b = b + 1
				if b >= (len(res1) - 1):
					break
			book_info[res1[a]] = res1[a + 1:b]
	# print book_info
	return book_info


def keywords(content):
	"""
	通过爬取网页中的meta信息,来获取keywords
	形如：
	地图（人文版）, （书名）
	(波兰)亚历山德拉·米热林斯卡,丹尼尔·米热林斯基 著, （作者）
	贵州人民出版社,
	2014-8,
	简介,
	作者,
	书评,
	论坛,
	推荐,
	二手
	"""
	# content = urllib.urlopen(
	# 	'https://book.douban.com/subject/25960141/').read()
	sel = etree.HTML(content)
	keywords = sel.xpath('/html/head/meta[5]/@content')[0]
	keywords = keywords.split(',')
	print 'keywords',keywords
	# for element in sel.xpath('//*[@id="info"]'):
	# 	print ''.join(element.xpath('descendant-or-self::text()'))
	# //*[@id="info"]/span[2]

	return keywords
