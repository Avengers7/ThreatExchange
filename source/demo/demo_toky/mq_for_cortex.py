import json
import greenstalk
from cortex4py.api import Api
from cortex4py.query import *

#连接cortex
api = Api('http://127.0.0.1:9001', 'o+BNB3MAspBWDNz5ov/4YgsSjXhJaV/e')

def analyzeIOC(ipaddress):
    # 获取可用的ip分析器
    ip_analyzers = api.analyzers.get_by_type('ip')
    jobs = []
    # 执行分析器
    for analyzer in ip_analyzers:
        job = api.analyzers.run_by_name(analyzer.name, {
            'data': ipaddress,
            'dataType': 'ip',
            'tlp': 1,
            'message': 'honeypot',
            }, force=1)
        jobs.append(job)

    count = 0
    while True:
        #等待所有任务执行完毕(成功或失败)
        for job in jobs:
            if api.jobs.get_by_id(job.id).status == 'Success':
                count = count + 1
            elif api.jobs.get_by_id(job.id).status == 'Failure':
                count = count + 1
            else:
                pass
        if count == len(jobs):
            break
        else:
            count = 0
    results = []
    for job in jobs:
        #获取分析结果
        report = api.jobs.get_report(job.id).report
        results.append(report.get('full', {}))
    return results


# 待分析任务消息队列

task_queue = greenstalk.Client('127.0.0.1', 11300,watch='cortex-task')

# 分析结果消息队列

result_queue = greenstalk.Client('127.0.0.1', 11300,use='cortex-result')

while True:
    #读取消息队列中等待分析的ip
    job = task_queue.reserve()
    task_queue.delete(job)
    #开始分析任务
    results = analyzeIOC(json.loads(job.body)["ip"])
    for result in results:
        #将结果写入消息队列
        result_queue.put(json.dumps({'data':str(result)}))