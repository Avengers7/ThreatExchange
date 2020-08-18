from gensim.models import Word2Vec
from sklearn.cluster import KMeans
#语料
sentences = [['this', 'is', 'a', 'pear'],
            ['this', 'is',  'a','banana'],
            ['this', 'is',  'an','apple'],
            ['this','is','a','lemon'],
            ['this','is','a','melon'],
            ['this','is','a','cherry']]
#训练词向量
model = Word2Vec(sentences, min_count=1)
wordvector = []
for key in model.wv.vocab.keys():
    #逐一获取每个词汇的对应词向量
    wordvector.append(model[key])
#通过余弦相似度获取与apple最近义的词
print (model.most_similar(positive=['apple'], negative=[], topn=2))
#结果为[('is', 0.19642898440361023), ('pear', 0.15730774402618408)]
#可见出现了pear，但仍有改善的余地

#使用kmeans算法对语料进行聚类，共分为2类
clf = KMeans(n_clusters=2)
clf.fit(wordvector)
labels = clf.labels_
classCollects={}
keys = model.wv.vocab.keys()
for i in range(len(keys)):
    if labels[i] in list(classCollects.keys()):
        classCollects[labels[i]].append(list(keys)[i])
    else:
        classCollects={0:[],1:[]}

print(classCollects[0])
print(classCollects[1])


'''
结果为：
['pear', 'banana', 'apple', 'lemon', 'melon']
['is', 'a', 'an', 'cherry']
'''