#!/usr/bin/env python3
"""
Unreal Engine 프로젝트용 compile_commands.json 생성기
프로젝트 구조를 스캔해서 직접 생성
"""

import json
import os
import sys
from pathlib import Path

def find_uproject(working_dir):
    """working_dir 또는 하위에서 .uproject 파일 찾기"""
    for f in Path(working_dir).glob("*.uproject"):
        return f
    for f in Path(working_dir).glob("*/*.uproject"):
        return f
    return None

def find_engine_dir(working_dir):
    """UnrealEngine 디렉토리 찾기"""
    candidates = [
        Path(working_dir) / "UnrealEngine",
        Path(working_dir).parent / "UnrealEngine",
        Path(working_dir) / "Engine",
    ]
    for p in candidates:
        if (p / "Engine" / "Source").exists():
            return p
    return None

def collect_source_files(project_dir, engine_dir):
    """프로젝트와 엔진의 소스 파일 수집"""
    source_files = []

    # 프로젝트 소스
    project_source = project_dir / "Source"
    if project_source.exists():
        for cpp in project_source.rglob("*.cpp"):
            source_files.append(cpp)

    # 플러그인 소스
    plugins_dir = project_dir / "Plugins"
    if plugins_dir.exists():
        for cpp in plugins_dir.rglob("*.cpp"):
            source_files.append(cpp)

    return source_files

def get_include_paths(project_dir, engine_dir):
    """Include 경로 수집"""
    includes = []

    # 엔진 기본 경로
    engine_source = engine_dir / "Engine" / "Source"
    if engine_source.exists():
        includes.append(engine_source)

        # Runtime 모듈들
        runtime = engine_source / "Runtime"
        if runtime.exists():
            for module_dir in runtime.iterdir():
                if module_dir.is_dir():
                    public = module_dir / "Public"
                    classes = module_dir / "Classes"
                    if public.exists():
                        includes.append(public)
                    if classes.exists():
                        includes.append(classes)
                    includes.append(module_dir)

        # Developer 모듈들
        developer = engine_source / "Developer"
        if developer.exists():
            for module_dir in developer.iterdir():
                if module_dir.is_dir():
                    public = module_dir / "Public"
                    if public.exists():
                        includes.append(public)

    # 엔진 Generated 헤더
    engine_intermediate = engine_dir / "Engine" / "Intermediate" / "Build" / "Win64"
    if engine_intermediate.exists():
        for inc_dir in engine_intermediate.rglob("Inc"):
            if inc_dir.is_dir():
                includes.append(inc_dir)
                for sub in inc_dir.iterdir():
                    if sub.is_dir():
                        includes.append(sub)

    # 프로젝트 소스 경로
    project_source = project_dir / "Source"
    if project_source.exists():
        for module_dir in project_source.iterdir():
            if module_dir.is_dir():
                includes.append(module_dir)
                for sub in ["Public", "Private", "Classes"]:
                    subdir = module_dir / sub
                    if subdir.exists():
                        includes.append(subdir)

    # 프로젝트 Generated 헤더
    project_intermediate = project_dir / "Intermediate" / "Build" / "Win64"
    if project_intermediate.exists():
        # Development, Shipping 등 다양한 config에서 찾기
        for config_dir in project_intermediate.iterdir():
            if config_dir.is_dir():
                inc_dir = config_dir / "Inc"
                if inc_dir.exists():
                    for module_inc in inc_dir.iterdir():
                        if module_inc.is_dir():
                            includes.append(module_inc)

    # 프로젝트 플러그인
    plugins_dir = project_dir / "Plugins"
    if plugins_dir.exists():
        for source_dir in plugins_dir.rglob("Source"):
            if source_dir.is_dir():
                includes.append(source_dir)
                for sub in source_dir.iterdir():
                    if sub.is_dir():
                        includes.append(sub)
                        for subsub in ["Public", "Private", "Classes"]:
                            subsubdir = sub / subsub
                            if subsubdir.exists():
                                includes.append(subsubdir)

    # 엔진 플러그인
    engine_plugins = engine_dir / "Engine" / "Plugins"
    if engine_plugins.exists():
        for source_dir in engine_plugins.rglob("Source"):
            if source_dir.is_dir():
                includes.append(source_dir)

    # ThirdParty
    project_thirdparty = project_dir / "Source" / "ThirdParty"
    if project_thirdparty.exists():
        includes.append(project_thirdparty)
        for sub in project_thirdparty.rglob("*"):
            if sub.is_dir() and "include" in sub.name.lower():
                includes.append(sub)

    return list(set(includes))

def get_defines():
    """전처리기 정의"""
    return [
        "WITH_EDITOR=1",
        "WITH_ENGINE=1",
        "WITH_UNREAL_DEVELOPER_TOOLS=1",
        "WITH_PLUGIN_SUPPORT=1",
        "UE_BUILD_DEVELOPMENT=1",
        "UE_BUILD_MINIMAL=0",
        "IS_MONOLITHIC=0",
        "IS_PROGRAM=0",
        "PLATFORM_WINDOWS=1",
        "PLATFORM_64BITS=1",
        "UNICODE",
        "_UNICODE",
        "__UNREAL__",
        "UBT_COMPILED_PLATFORM=Windows",
        "CORE_API=",
        "COREUOBJECT_API=",
        "ENGINE_API=",
        "SLATE_API=",
        "SLATECORE_API=",
        "INPUTCORE_API=",
    ]

def generate_compile_commands(working_dir, output_path=None):
    working_dir = Path(working_dir)

    uproject = find_uproject(working_dir)
    if not uproject:
        print("No .uproject file found")
        return False

    project_dir = uproject.parent
    project_name = uproject.stem
    print(f"Project: {project_name} at {project_dir}")

    engine_dir = find_engine_dir(working_dir)
    if not engine_dir:
        print("UnrealEngine directory not found")
        return False
    print(f"Engine: {engine_dir}")

    # 소스 파일 수집
    print("Collecting source files...")
    source_files = collect_source_files(project_dir, engine_dir)
    print(f"Found {len(source_files)} source files")

    # Include 경로 수집
    print("Collecting include paths...")
    include_paths = get_include_paths(project_dir, engine_dir)
    print(f"Found {len(include_paths)} include paths")

    # 정의 수집
    defines = get_defines()

    # 컴파일 명령 생성
    compile_commands = []

    # 기본 플래그
    base_flags = [
        "clang++",
        "-std=c++17",
        "-x", "c++",
        "-ferror-limit=0",
        "-Wall",
        "-Wno-unknown-pragmas",
        "-Wno-unused-private-field",
    ]

    # Include 플래그
    include_flags = [f"-I{p}" for p in include_paths]

    # Define 플래그
    define_flags = [f"-D{d}" for d in defines]

    all_flags = base_flags + define_flags + include_flags

    for source_file in source_files:
        entry = {
            "directory": str(working_dir),
            "file": str(source_file),
            "arguments": all_flags + ["-c", str(source_file)]
        }
        compile_commands.append(entry)

    # 출력
    if output_path is None:
        output_path = working_dir / "compile_commands.json"
    else:
        output_path = Path(output_path)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(compile_commands, f, indent=2)

    print(f"Generated {output_path} with {len(compile_commands)} entries")
    return True

if __name__ == "__main__":
    working_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    success = generate_compile_commands(working_dir, output_path)
    sys.exit(0 if success else 1)
