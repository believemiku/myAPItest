#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API测试框架主入口
支持运行测试套件、单独测试用例，并生成Allure报告
"""

import argparse
import os
import sys
import subprocess
import shutil


def clean_directories():
    """清理旧的测试结果和报告目录"""
    directories = ['allure-results', 'allure-report', '.pytest_cache']
    for directory in directories:
        if os.path.exists(directory):
            shutil.rmtree(directory, ignore_errors=True)
            print(f"已清理目录: {directory}")


def run_tests(suite_path=None, test_path=None, markers=None, verbose=True, parallel=0):
    """运行测试"""
    # 构建pytest命令
    cmd = ['python', '-m', 'pytest']
    
    # 添加测试路径
    if suite_path:
        cmd.append(suite_path)
    elif test_path:
        cmd.append(test_path)
    else:
        # 默认运行所有测试
        cmd.append('tests/suites')
    
    # 添加标记过滤
    if markers:
        cmd.extend(['-m', markers])
    
    # 添加详细输出
    if verbose:
        cmd.append('-v')
    
    # 添加并行执行参数
    if parallel > 0:
        cmd.extend(['-n', str(parallel)])
    elif parallel == 0:
        # 自动检测并行进程数
        cmd.extend(['-n', 'auto'])
    
    print(f"执行命令: {' '.join(cmd)}")
    
    # 运行测试
    result = subprocess.run(cmd, capture_output=False)
    
    return result.returncode == 0


def generate_report():
    """生成Allure报告"""
    if not os.path.exists('allure-results'):
        print("警告: 没有找到allure-results目录，无法生成报告")
        return False
    
    cmd = 'allure generate allure-results -o allure-report --clean'
    print(f"生成报告: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    
    if result.returncode == 0:
        print("报告生成成功: allure-report/index.html")
        return True
    else:
        print("报告生成失败")
        return False


def open_report():
    """打开Allure报告"""
    report_path = os.path.abspath('allure-report/index.html')
    if os.path.exists(report_path):
        print(f"打开报告: {report_path}")
        if sys.platform == 'win32':
            os.startfile(report_path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', report_path])
        else:
            subprocess.run(['xdg-open', report_path])
    else:
        print("警告: 报告文件不存在，请先生成报告")


# def analyze_results():
#     """分析测试结果"""
#     from core.analyzer import TestAnalyzer
#     
#     analyzer = TestAnalyzer()
#     if analyzer.load_results():
#         return analyzer.generate_report()
#     return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='API测试框架主入口')
    
    # 测试选择参数
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--suite', '-s', type=str, help='运行指定的测试套件文件')
    group.add_argument('--test', '-t', type=str, help='运行指定的测试用例文件')
    group.add_argument('--all', '-a', action='store_true', help='运行所有测试')
    
    # 标记参数
    parser.add_argument('--markers', '-m', type=str, help='运行带有指定标记的测试用例')
    
    # 报告参数
    parser.add_argument('--report', '-r', action='store_true', help='生成Allure报告')
    parser.add_argument('--open', '-o', action='store_true', help='打开Allure报告')
    parser.add_argument('--no-clean', action='store_true', help='不清理旧的测试结果和报告')
    
    # 其他参数
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式，减少输出')
    parser.add_argument('--env', type=str, default='dev', help='指定测试环境 (dev, test, prod)')
    parser.add_argument('--parallel', '-p', type=int, default=0, help='并行执行测试的进程数，0表示自动')
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ['TEST_ENV'] = args.env
    print(f"设置测试环境为: {args.env}")
    
    # 清理旧的测试结果和报告
    if not args.no_clean:
        print("清理旧的测试结果和报告...")
        clean_directories()
    
    # 运行测试
    print("\n开始运行测试...")
    success = run_tests(
        suite_path=args.suite,
        test_path=args.test,
        markers=args.markers,
        verbose=not args.quiet,
        parallel=args.parallel
    )
    
    if success:
        print("\n测试执行成功！")
    else:
        print("\n测试执行失败！")
        sys.exit(1)
    
    # 生成报告
    if args.report:
        print("\n生成Allure报告...")
        if generate_report():
            print("报告生成完成")
            
            # 分析测试结果已移除
            # print("\n分析测试结果...")
            # analyze_results()
            
            # 打开报告
            if args.open:
                open_report()
    elif args.open:
        # 只打开报告，不生成
        open_report()


if __name__ == '__main__':
    main()