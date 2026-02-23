#!/usr/bin/env python3
"""
MSBuild 빌드 로그에서 compile_commands.json 생성
사용법:
1. msbuild /v:detailed /fl 로 빌드 (msbuild.log 생성)
2. python msbuild-to-compile-commands.py msbuild.log
"""

import json
import re
import sys
import os
from pathlib import Path

def parse_msbuild_log(log_path):
    compile_commands = []

    # cl.exe 호출 패턴
    cl_pattern = re.compile(
        r'^\s*(?:[\d:>]+)?\s*(?:ClCompile:)?\s*'
        r'(?:.*?\\)?cl\.exe\s+(.+)$',
        re.IGNORECASE | re.MULTILINE
    )

    # /c 옵션과 소스 파일 패턴
    source_pattern = re.compile(r'["\']?([^"\']+\.cpp)["\']?', re.IGNORECASE)

    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # 각 cl.exe 호출 찾기
    for match in cl_pattern.finditer(content):
        args = match.group(1)

        # 소스 파일 찾기
        source_files = []
        for part in args.split():
            if part.lower().endswith('.cpp') or part.lower().endswith('.c'):
                # 따옴표 제거
                source_file = part.strip('"\'')
                if os.path.isabs(source_file):
                    source_files.append(source_file)

        if not source_files:
            continue

        # 디렉토리 추출
        directory = os.path.dirname(source_files[0]) if source_files else os.getcwd()

        for source_file in source_files:
            entry = {
                "directory": directory,
                "command": f"cl.exe {args}",
                "file": source_file
            }
            compile_commands.append(entry)

    return compile_commands

def parse_sndbs_output(log_path):
    """SNDBS (SN-DBS) 분산 빌드 시스템 로그 파싱"""
    compile_commands = []

    # SNDBS는 다른 형식의 로그를 생성
    # [N/M] Compile Module.xxx.cpp 형식
    compile_pattern = re.compile(
        r'\[[\d/]+\]\s+Compile\s+(.+\.cpp)',
        re.IGNORECASE
    )

    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            match = compile_pattern.search(line)
            if match:
                source_file = match.group(1).strip()
                # 실제 경로를 찾아야 함
                compile_commands.append({
                    "file": source_file,
                    "arguments": ["clang++", "-c", source_file],
                    "directory": os.getcwd()
                })

    return compile_commands

def main():
    if len(sys.argv) < 2:
        print("Usage: python msbuild-to-compile-commands.py <msbuild.log> [output.json]")
        print("\nTo generate the log:")
        print("  msbuild YourProject.sln /v:detailed /fl")
        sys.exit(1)

    log_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "compile_commands.json"

    if not os.path.exists(log_path):
        print(f"Error: Log file not found: {log_path}")
        sys.exit(1)

    print(f"Parsing {log_path}...")
    compile_commands = parse_msbuild_log(log_path)

    if not compile_commands:
        print("No compile commands found in MSBuild log.")
        print("Trying SNDBS format...")
        compile_commands = parse_sndbs_output(log_path)

    if compile_commands:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(compile_commands, f, indent=2)
        print(f"Generated {output_path} with {len(compile_commands)} entries")
    else:
        print("No compile commands found.")
        print("Make sure to build with: msbuild /v:detailed /fl")
        sys.exit(1)

if __name__ == "__main__":
    main()
