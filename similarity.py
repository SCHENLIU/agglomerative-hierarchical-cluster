#coding:utf-8
from dssm_client import DssmClient
import math
import numpy as np
import sklearn.metrics.pairwise

def cosine_similarity(x, y):
    num = x.dot(y.T)
    denom = np.linalg.norm(x) * np.linalg.norm(y)
    return num / denom

def get_vec(nc, data):
    res = nc.dssm(data)
    print(res, "AAAAA")
    title_dssm_vec = res.title_dssm_vec
    title_dssm_vec = [float(item) for item in title_dssm_vec[2:-2].split(', ')]
    return np.array(title_dssm_vec)

if __name__ == '__main__':
    nc = DssmClient(host='multi-dssm-server.nlp.data.sina.com.cn', fixHost=True, timeout=6000, port=80)
    data1 = {'title': '李国庆撬开保险柜拿走资料，警方通报来了：行政拘留', 'content': ' ', 'model': 'news_dssm'}
    data2 = {'title': '李国庆被北京朝阳公安分局依法行政拘留', 'content': ' ', 'model': 'news_dssm'}
    res_1 = get_vec(nc, data1)
    res_2 = get_vec(nc, data2)
    print(res_1)
    print(res_2)
    print(cosine_similarity(res_1, res_2))
