" videm settings
" Author:   fanhe <fanhed@163.com>
" License:  GPLv2
" Create:   2013-04-22
" Change:   2013-05-18

" 选项结构，'.' 作为分隔符，如 .videm.wsp.LinkToEditor

let s:settings = {}

function! videm#settings#Set(opt, val) "{{{2
    let li = split(a:opt, '\.')
    if empty(li)
        return
    endif

    let d = s:settings
    for k in li[:-2]
        if !has_key(d, k)
            let d[k] = {}
        endif
        if type(d[k]) != type({}) " 如果非页结点不是字典的话，参数非法
            return
        endif
        let d = d[k]
    endfor
    let d[li[-1]] = a:val
endfunction
"}}}2
function! videm#settings#Get(opt, ...) "{{{2
    let li = split(a:opt, '\.')
    if empty(li)
        return s:settings
    endif

    let d = s:settings
    for k in li[:-2]
        if !has_key(d, k)
            return get(a:000, 0, 0)
        endif
        if type(d[k]) != type({})
            return get(a:000, 0, 0)
        endif
        let d = d[k]
    endfor
    return get(d, li[-1], get(a:000, 0, 0))
endfunction
"}}}2
function! videm#settings#Has(opt) "{{{2
    let li = split(a:opt, '\.')
    if empty(li)
        return 0
    endif

    let d = s:settings
    for k in li[:-2]
        if !has_key(d, k)
            return 0
        endif
        if type(d[k]) != type({})
            return 0
        endif
        let d = d[k]
    endfor
    return has_key(d, li[-1])
endfunction
"}}}2
" opts 是字典，{'path': value, ...}
function! videm#settings#Init(opts) "{{{2
    for item in items(a:opts)
        if !videm#settings#Has(item[0])
            call videm#settings#Set(item[0], item[1])
        endif
    endfor
endfunction
"}}}2

" vim: fdm=marker fen et sw=4 sts=4 fdl=1
