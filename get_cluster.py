#coding:utf-8
from dssm_client import DssmClient
import json
import time
import numpy as np
import model.cluster as cluster
import os
from similarity import cosine_similarity
import collections
import time

c = collections.Counter()

_cur_dir = os.path.dirname(os.path.realpath(__file__))

class config():
    def __init__(self):
        self.result_dir = os.path.join(_cur_dir, 'result')
        self.cluster_number = 25
        self.input_file = '0708data_1.csv'
        self.redian_dir = os.path.join(_cur_dir, 'redian')
        self.timescope = 86400
        self.vector_len = 128

def sentence_embedding(input_data):
    nc = DssmClient(host='multi-dssm-server.nlp.data.sina.com.cn', fixHost=True, timeout=6000, port=80)
    # data = {'title': ' ', 'content': ' ', 'model': 'albert_dssm'}
    data = {'title': ' ', 'content': ' ', 'model': 'news_dssm'}
    output_data = []
    for item in input_data:
        if len(item) != 16: continue
        title = item[4].replace("\"", "")
        crawl_time = item[-2]
        data['title'] = title

        retry = 0
        kws = nc.dssm(data)

        while not kws.title_dssm_vec and retry < 11:
            kws = nc.dssm(data)
            retry += 1
        title_dssm_vec = kws.title_dssm_vec
        title_dssm_vec = [float(r) for r in title_dssm_vec[2:-2].split(', ')]
        timeArray = time.strptime(crawl_time[1:-1], '%Y-%m-%d %H:%M:%S')
        output_data.append([crawl_time, title, title_dssm_vec, int(time.mktime(timeArray)), item[6]])
    return output_data

def eucliDist(A,B):
    return np.sqrt(sum(np.power((A - B), 2)))

def train(config, X):
    print(X.shape)
    n_clusters = len(feature)//2 if len(feature) <= config.cluster_number*4 else config.cluster_number
    n_clusters = max(1, n_clusters)
    clst = cluster.AgglomerativeClustering(n_clusters=n_clusters, linkage='complete', affinity='cosine')
    print("Training...")
    begin = time.time()
    labels = clst.fit_predict(X)
    n_clusters = clst.n_clusters
    end = time.time()
    print("Done.", end - begin)
    return labels, n_clusters

if __name__=='__main__':
    config = config()
    with open(config.input_file, 'r') as fr:
        data = [r.strip().split(',') for r in fr]

    print("Getting sentence embedded:")
    embedding_data = sentence_embedding(data)
    print("Done")

    embedding_data.sort(key=lambda a: a[3])
    # with open('middleresult.txt', 'w') as fw:
    #     fw.write('\n'.join([r[1] for r in embedding_data]))
    print(len(embedding_data))
    index = 0
    pre_centre = np.zeros(shape=(0,config.vector_len))
    while index < len(embedding_data):
        #per 30mins data generate
        end = index
        while end < len(embedding_data) and embedding_data[end][3] < embedding_data[index][3] + config.timescope:
            end += 1

        #train
        print('Trainning, time scope:', str(index) + '-' + str(end))
        train_data = embedding_data[index:end]
        feature = [r[2] for r in train_data]
        feature = np.array(feature)
        if len(feature) > 1:
            labels, n_clusters = train(config, feature)
        else:
            labels, n_clusters = [0], 1
        new = []
        old = []
        #find new centre
        cur_centre = np.zeros(shape=(0,config.vector_len))
        for i in range(n_clusters):
            #average centre
            #classe_i = np.argwhere(labels==i)
            #cur_centre_item = np.mean(feature[classe_i], axis=0)

            #min-distance centre
            classe_i = np.argwhere(labels == i)
            mean_centre = np.mean(feature[classe_i], axis=0)
            eudistance = np.array([eucliDist(mean_centre[0], r[0]) for r in feature[classe_i]])
            min_centre = classe_i[np.argmin(eudistance)]
            min_centre = min_centre[0]

            is_old = 0
            cur_centre = np.concatenate((cur_centre, [feature[min_centre]]), axis=0)
            if pre_centre.any():
                for item in pre_centre:
                    cos_value = cosine_similarity(item, feature[min_centre])
                    if cos_value > 0.8:
                        old.append(train_data[min_centre]+[str(labels[min_centre])])
                        is_old = 1
                        break
            if not is_old: new.append(train_data[min_centre]+[str(labels[min_centre])])
        pre_centre = cur_centre

        # write cluster result
        write_data = []
        print(train_data[0])
        for i, item in enumerate(train_data):
            item.append(labels[i])
            write_data.append(item)
        write_data.sort(key= lambda a:a[-1])
        write_data = ['\t'.join([l[0], l[4], l[1], str(l[5])]) for l in write_data]
        print(os.path.join(config.result_dir, str(index) + '-' + str(end)))
        fw = open(os.path.join(config.result_dir, str(index) + '-' + str(end) + '.txt'), 'w')
        fw.write('\n'.join(write_data))
        fw.close()

        # wirte changing hot news
        new.sort(key= lambda a:a[-1])
        new = ['\t'.join([l[0], l[4], l[1], str(l[5])]) for l in new]
        old.sort(key= lambda a:a[-1])
        old = ['\t'.join([l[0], l[4], l[1], str(l[5])]) for l in old]
        print(os.path.join(config.redian_dir, str(index) + '-' + str(end)))
        fw = open(os.path.join(config.redian_dir, str(index) + '-' + str(end) + '.txt'), 'w')
        fw.write('new:' + '\n' + '\n'.join(new))
        fw.write('\n' + 'old:' + '\n' + '\n'.join(old))
        fw.close()

        index = end
