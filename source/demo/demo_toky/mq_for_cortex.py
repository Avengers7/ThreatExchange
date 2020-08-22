import json
import greenstalk
from cortex4py.api import Api
from cortex4py.query import *
#连接cortex


def analyze_ip_ioc(ipaddress, api_info):
    """
    调用Cortex中全部可用分析器来孵化IP信息
    :param ipaddress: 需要进行信息孵化的IP
    :param api_info: API信息，API(IP, API key)
    :return: 经过分析器孵化，并且进行IOC格式标准化后的IOC信息
    """

    # 取得Cortex中全部可用的分析器
    ip_analyzers = api_info.analyzers.get_by_type('ip')
    jobs = []
    # 执行分析器
    for analyzer in ip_analyzers:
        job = api_info.analyzers.run_by_name(analyzer.name, {
            'data': ipaddress,
            'dataType': 'ip',
            'tlp': 1,
            }, force=1)
        jobs.append(job)

    count = 0
    while True:
        for job in jobs:
            if api_info.jobs.get_by_id(job.id).status == 'Success':
                count = count + 1
            elif api_info.jobs.get_by_id(job.id).status == 'Failure':
                count = count + 1
            else:
                pass
        if count == len(jobs):
            break
        else:
            count = 0
    results = []
    for job_element in jobs:
        element_id = job_element.id
        report = api_info.jobs.get_report(element_id).report
        results.append(report.get('full', {}))

    return results


if __name__ == '__main__':

    api = Api('http://127.0.0.1:9001', 'o+BNB3MAspBWDNz5ov/4YgsSjXhJaV/e')

    # 待分析任务消息队列
    task_queue = greenstalk.Client('172.16.133.133', 11300, watch='cortex-task')

    # 分析结果消息队列
    result_queue = greenstalk.Client('172.16.133.133', 11300, use='cortex-result')

    while True:
        # 读取消息队列中等待分析的ip
        job = task_queue.reserve()
        task_queue.delete(job)
        # 开始分析任务
        results = analyze_ip_ioc("196.11.180.201", api_info=api)
        for result in results:
            # 将结果写入消息队列
            result_queue.put(json.dumps({'data': str(result)}))
