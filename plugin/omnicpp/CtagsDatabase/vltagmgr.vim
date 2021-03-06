" tags manager plugin
" Author:   fanhe <fanhed@163.com>
" License:  GPLv2
" Create:   2011-05-10
" Change:   2013-05-19

if exists('g:loaded_vltagmgr')
    finish
endif
let g:loaded_vltagmgr = 1

let s:start = 0

command! -nargs=* -complete=file VTMParseFiles call g:VTMParseFiles(<f-args>)

function s:InitVariable(varName, defaultVal) "{{{2
    if !exists(a:varName)
		let {a:varName} = a:defaultVal
        return 1
    endif
    return 0
endfunction
"}}}

call s:InitVariable('g:VimTagsManager_DbFile', 'vltags.db')

call s:InitVariable('g:VimTagsManager_SrcDir', expand('~/.videm/core'))

call s:InitVariable('g:VimTagsManager_InclAllCondCmplBrch', 1)

let s:hasStarted = 0

function! g:GetTagsByScopeAndKind(scope, kind) "{{{2
    py vim.command("let tags = %s" % ToVimEval(vtm.GetTagsByScopeAndKind(
                \vim.eval('a:scope'), vim.eval('a:kind'))))
    return tags
endfunction


function! g:GetTagsByScopesAndKinds(scopes, kinds) "{{{2
    py vim.command("let tags = %s" % ToVimEval(vtm.GetTagsByScopesAndKinds(
                \vim.eval('a:scopes'), vim.eval('a:kinds'))))
    return tags
endfunction


function! g:GetTagsByScopeAndName(scope, name) "{{{2
    py vim.command("let tags = %s" % ToVimEval(vtm.GetTagsByScopeAndName(
                \vim.eval('a:scope'), vim.eval('a:name'))))
    return tags
endfunction
"}}}
" 可选参数控制是否允许部分匹配(且不区分大小写), 默认允许
function! g:GetTagsByScopesAndName(scopes, name, ...) "{{{2
    let bPartialMatch = a:0 > 0 ? a:1 : 1
    py vim.command("let tags = %s" % ToVimEval(vtm.GetTagsByScopeAndName(
                \vim.eval('a:scopes'), vim.eval('a:name'),
                \int(vim.eval('bPartialMatch')))))
    return tags
endfunction
"}}}
" 可选参数控制是否允许部分匹配(且不区分大小写), 默认允许
function! g:GetOrderedTagsByScopesAndName(scopes, name, ...) "{{{2
    let bPartialMatch = a:0 > 0 ? a:1 : 1
    py vim.command("let tags = %s" % ToVimEval(vtm.GetOrderedTagsByScopesAndName(
                \vim.eval('a:scopes'), vim.eval('a:name'),
                \int(vim.eval('bPartialMatch')))))
    return tags
endfunction
"}}}
function! g:GetTagsByPath(path) "{{{2
    py vim.command("let tags = %s" 
                \% ToVimEval(vtm.GetTagsByPath(vim.eval('a:path'))))
    return tags
endfunction

function! g:GetTagsByKindAndPath(kind, path) "{{{2
    py vim.command("let tags = %s" % ToVimEval(vtm.GetTagsByKindAndPath(
                \vim.eval('a:kind'), vim.eval('a:path'))))
    return tags
endfunction

function! g:VTMParseFiles(...) "{{{2
    if exists('s:hasConnected')
        if !s:hasConnected
            py vtm.OpenDatabase(vim.eval('s:absDbFile'))
        endif
    else
        echohl WarningMsg
        echo 'VimTagsManager has not yet started!'
        echohl None
        return
    endif

    "若传进来的第一个参数为列表, 仅解析此列表
    if a:0 > 0
        if type(a:1) == type([])
            py vtm.ParseFiles(vim.eval('a:1'))
            return
        endif
    endif

    py vtm.ParseFiles(vim.eval('a:000'))
endfunction
"}}}
function! vltagmgr#GetTagsBySql(sql) "{{{2
    py vim.command("let tags = %s"
            \       % ToVimEval(vtm.GetTagsBySql(vim.eval("a:sql"))))
    return tags
endfunction
"}}}
function! vltagmgr#OpenDatabase(dbFile) "{{{2
    if !s:hasStarted
        call vltagmgr#Init()
    endif

    py vtm.OpenDatabase(os.path.expanduser(vim.eval('a:dbFile')))
endfunction
"}}}
function! vltagmgr#Init() "{{{2
    if s:hasStarted
        return
    else
        let s:hasStarted = 1
    endif

python << PYTHON_EOF
# -*- encoding:utf-8 -*-
import sys
import os
import os.path
import vim

#try:
#    sys.path.index(os.path.expanduser(vim.eval('g:VimTagsManager_SrcDir')))
#except ValueError:
#    sys.path.append(os.path.expanduser(vim.eval('g:VimTagsManager_SrcDir')))
from omnicpp.VimTagsManager import VimTagsManager
from omnicpp.VimTagsManager import AppendCtagsOpt
from Misc import ToVimEval

# 添加选项
if vim.eval('g:VimTagsManager_InclAllCondCmplBrch') != '0':
    AppendCtagsOpt('-m')

PYTHON_EOF

    py vtm = VimTagsManager()
    if filereadable(g:VimTagsManager_DbFile)
        " 若已存在数据库文件, 直接打开之
        let s:hasConnected = 1
        py vtm.OpenDatabase(
                \ os.path.expanduser(vim.eval('g:VimTagsManager_DbFile')))
    else
        " 没有存在的数据库文件, 暂时连接内存数据库
        " 当请求 ParseFiles() 时才新建硬盘的数据库
        let s:hasConnected = 0
        py vim.command("let s:absDbFile = '%s'" 
                \   % os.path.abspath(os.path.expanduser(vim.eval(
                \           'g:VimTagsManager_DbFile'))).replace("'", "''"))
        " 连接内存数据库
        py vtm.OpenDatabase(':memory:')
    endif
endfunction
"}}}
" vim:fdm=marker:fen:expandtab:smarttab:fdl=1:
