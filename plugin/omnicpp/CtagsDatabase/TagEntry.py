#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import re
from Misc import Obj2Dict, Dict2Obj

CKinds = {
    'c': "class",     
    'd': "macro",     
    'e': "enumerator",
    'f': "function",  
    'g': "enum",      
    'l': "local",     
    'm': "member",    
    'n': "namespace", 
    'p': "prototype", 
    's': "struct",    
    't': "typedef",   
    'u': "union",     
    'v': "variable",  
    'x': "externvar", 
}

RevCKinds = {
    "class":        'c',
    "macro":        'd',
    "enumerator":   'e',
    "function":     'f',
    "enum":         'g',
    "local":        'l',
    "member":       'm',
    "namespace":    'n',
    "prototype":    'p',
    "struct":       's',
    "typedef":      't',
    "union":        'u',
    "variable":     'v',
    "externvar":    'x',
}

def ToFullKind(kind):
    result = kind
    if CKinds.has_key(kind):
        result = CKinds[kind]
    return result
def ToFullKinds(kinds):
    return [ ToFullKind(kind) for kind in kinds ]


def ToAbbrKind(kind):
    result = kind
    if RevCKinds.has_key(kind):
        result = RevCKinds[kind]
    return result
def ToAbbrKinds(kinds):
    return [ ToAbbrKind(kind) for kind in kinds ]

reMacroSig = r'^\s*#\s*define\s*[a-zA-Z_]\w*(\(.*?\))' # 包括括号
patMacroSig = re.compile(reMacroSig)
def GetMacroSignature(srcLine):
    global patMacroSig
    m = patMacroSig.match(srcLine)
    if m:
        return m.group(1)
    else:
        return ''

pat1 = re.compile(r'\s*\b(?:::\s*)?(?:[a-zA-Z_]\w*\s*::\s*)*[a-zA-Z_]\w*\s*\(.*')
pat2 = re.compile(r'template\s*<.*>\s*')

class TagEntry():
    def __init__(self):
        self.id = -1                # unused

        self.name = ''              # Tag name (short name, excluding any scope 
                                    # names)
        self.file = ''              # File this tag is found
        self.line = -1              # Line number
        self.text = ''              # code text

        self.pattern = ''           # A pattern that can be used to locate the 
                                    # tag in the file

        self.kind = '<unknown>'     # Member, function, class, typedef etc.
        self.parent = ''            # Direct parent
        self.path = ''              # Tag full path
        self.scope = ''             # Scope

        self.exts = {}              # Additional extension fields

        self.differOnByLineNumber = False

    #def __eq__(self, rhs):
        #res2 = self.scope == rhs.scope \
                #and self.file == rhs.file \
                #and self.kind == rhs.kind \
                #and self.parent == rhs.parent \
                #and self.pattern == rhs.pattern \
                #and self.name == rhs.name \
                #and self.path == rhs.path \
                #and self.GetInheritsAsString() == rhs.GetInheritsAsString() \
                #and self.GetAccess() == rhs.GetAccess() \
                #and self.GetSignature() == rhs.GetSignature() \
                #and self.GetTyperef() == rhs.GetTyperef()
        #res = res2 and self.line == rhs.line

        #if res2 and not res:
            ## the entries are differs only in the line numbers
            #self.differOnByLineNumber = True

        #return res

    def ToDict(self):
        return Obj2Dict(self, set(['differOnByLineNumber']))

    def FromDict(self, d):
        Dict2Obj(self, d)

    def Create(self, name, fileName, line, text, kind, exts, pattern = ''):
        self.SetId(-1)
        self.SetName(name)
        self.SetFile(fileName)
        self.SetLine(line)
        self.SetText(text)
        if kind:
            self.SetKind(kind)
        else:
            self.SetKind('<unknown>')
        self.exts = exts
        self.SetPattern(pattern) # unused

        # Check if we can get full name (including path)
        # 添加 parentType 属性, 以保证不丢失信息
        scope = self.GetExtField('class')
        if scope:
            self.SetParentType('class')
            self.UpdatePath(scope)
        else:
            scope = self.GetExtField('struct')
            if scope:
                self.SetParentType('struct')
                self.UpdatePath(scope)
            else:
                scope = self.GetExtField('namespace')
                if scope:
                    self.SetParentType('namespace')
                    self.UpdatePath(scope)
                else:
                    scope = self.GetExtField('interface')
                    if scope:
                        self.SetParentType('interface')
                        self.UpdatePath(scope)
                    else:
                        scope = self.GetExtField('union')
                        if scope:
                            self.SetParentType('union')
                            self.UpdatePath(scope)
                        # added on 2012-05-17
                        else:
                            scope = self.GetExtField('enum')
                            if scope:
                                self.SetParentType('enum')
                                # enumerator 的 scope 和 path 要退一级
                                scope = '::'.join(scope.split('::')[:-1])
                                self.UpdatePath(scope)

        if scope:
            self.SetScope(scope)
        else:
            self.SetScope('<global>')

        # If there is no path, path is set to name
        if not self.GetPath():
            self.SetPath(self.GetName())

        # Get the parent name
        tok = self.GetPath().split('::')
        if len(tok) < 2:
            parent = '<global>'
        else:
            parent = tok[-2]
        self.SetParent(parent)

        if kind == 'macro':
            sig = GetMacroSignature(pattern[2:-2])
            if sig:
                self.SetSignature(sig)
        if kind == 'function' or kind == 'prototype':
            # NOTE: 应该足够准确了吧...
            global pat1, pat2
            retVal = pat1.sub('', text)
            #retVal = pat2.sub('', retVal)
            # 跳过 template<...>
            if retVal.startswith('template'):
                idx = 0
                for c in retVal:
                    idx += 1
                    if c == '<':
                        break
                nestLv = 1
                idx += 1
                for i, c in enumerate(retVal[idx: ]):
                    if c == '<':
                        nestLv += 1
                    elif c == '>':
                        nestLv -= 1
                        if nestLv == 0:
                            idx += i + 1
                            break
                retVal = retVal[idx:].strip()

            # 除去了模版信息的原始文本
            self.SetReturn(retVal)
        # TODO: 变量的 typeref 域


    def FromLine(self, strLine):
        strLine = strLine
        line = -1
        text = ''
        exts = {}

        # get the token name
        partStrList = strLine.partition('\t')
        name = partStrList[0]
        strLine = partStrList[2]

        # get the file name
        partStrList = strLine.partition('\t')
        fileName = partStrList[0]
        strLine = partStrList[2]

        # here we can get two options:
        # pattern followed by ;"
        # or
        # line number followed by ;"
        # 不准确, 必须带 '\t' 判断
        # partStrList = strLine.partition(';"')
        partStrList = strLine.partition(';"\t')
        if not partStrList[1]:
            # invalid pattern found
            return

        if strLine.startswith('/^'):
            # regular expression pattern found
            pattern = partStrList[0]
            strLine = '\t' + partStrList[2]
        else:
            # line number pattern found, this is usually the case when
            # dealing with macros in C++
            pattern = partStrList[0].strip()
            strLine = '\t' + partStrList[2]
            line = int(pattern)

        # next is the kind of the token
        if strLine.startswith('\t'):
            strLine = strLine.lstrip('\t')

        partStrList = strLine.partition('\t')
        kind = partStrList[0]
        strLine = partStrList[2]

        if strLine:
            for i in strLine.split('\t'):
                key = i.partition(':')[0].strip()
                val = i.partition(':')[2].strip()

                if key == 'line' and val:
                    line = int(val)
                elif key == 'text': # 不把 text 放到扩展域里面
                    text = val
                else:
                    exts[key] = val

        # 真的需要?
        #kind = kind.strip()
        #name = name.strip()
        #fileName = fileName.strip()
        #pattern = pattern.strip()

        if kind == 'enumerator':
            # enums are specials, they are not really a scope so they should 
            # appear when I type: enumName::
            # they should be member of their parent 
            # (which can be <global>, or class)
            # but we want to know the "enum" type they belong to, 
            # so save that in typeref,
            # then patch the enum field to lift the enumerator into the 
            # enclosing scope.
            # watch out for anonymous enums -- leave their typeref field blank.
            if exts.has_key('enum'):
                typeref = exts['enum']
                # comment on 2012-05-17
                #exts['enum'] = \
                        #exts['enum'].rpartition(':')[0].rpartition(':')[0]
                if not typeref.rpartition(':')[2].startswith('__anon'):
                    # watch out for anonymous enums
                    # just leave their typeref field blank.
                    exts['typeref'] = 'enum:%s' % typeref

        self.Create(name, fileName, line, text, kind, exts, pattern)

    def IsOk(self):
        return self.GetKind() != "<unknown>"

    def IsContainer(self):
        kind = self.GetKind()
        return kind == 'class' \
                or kind == 'struct' \
                or kind == 'union' \
                or kind == 'namespace' \
                or kind == 'project'

    def IsConstructor(self):
        if self.GetKind() != 'function' and self.GetKind() != 'prototype':
            return False
        else:
            return self.GetName() == self.GetScope()

    def IsDestructor(self):
        if self.GetKind() != 'function' and self.GetKind() != 'prototype':
            return False
        else:
            return self.GetName().startswith('~')

    def IsMethod(self):
        '''Return true of the this tag is a function or prototype'''
        return self.IsPrototype() or self.IsFunction()

    def IsFunction(self):
        return self.GetKind() == 'function'

    def IsPrototype(self):
        return self.GetKind() == 'prototype'

    def IsMacro(self):
        return self.GetKind() == 'macro'

    def IsClass(self):
        return self.GetKind() == 'class'

    def IsStruct(self):
        return self.GetKind() == 'struct'

    def IsScopeGlobal(self):
        return not self.GetScope() or self.GetScope() == '<global>'

    def IsTypedef(self):
        return self.GetKind() == 'typedef'


    #------------------------------------------
    # Operations
    #------------------------------------------
    def GetDifferOnByLineNumber(self):
        return self.differOnByLineNumber

    def GetId(self):
        return self.id
    def SetId(self, id):
        self.id = id

    def GetName(self):
        return self.name
    def SetName(self, name):
        self.name = name

    def GetText(self):
        return self.text
    def SetText(self, text):
        self.text = text

    def GetPath(self):
        return self.path
    def SetPath(self, path):
        self.path = path

    def GetFile(self):
        return self.file
    def SetFile(self, file):
        self.file = file

    def GetLine(self):
        return self.line
    def SetLine(self, line):
        self.line = line

    def GetPattern(self):
        # since ctags's pattern is regex, forward slashes are escaped. 
        # ('/' becomes '\/')
        pattern = self.pattern.replace('\\\\', '\\').replace('\\/', '/')

        # 尽最大努力转为 'utf-8' 编码
        if isinstance(pattern, unicode):
            pattern = pattern.encoding('utf-8')
        else:
            try:
                import chardet
                result = chardet.detect(pattern)
                confidence = result['confidence']
                encoding = result['encoding']
                if encoding and encoding != 'utf-8' and encoding != 'ascii':
                    if confidence < 0.9:
                        # 还是有可能检测错误, 可以把数字提高至 0.95
                        encoding = 'GB2312'

                    try:
                        pattern = pattern.decode(encoding).encode('utf-8')
                    except LookupError:
                        # FIXME: 编码不支持?!
                        #pattern = 'LookupError: '+ encoding
                        pass
                    except UnicodeDecodeError:
                        # TODO: 直接剔除注释即可
                        #pattern = 'UnicodeDecodeError: ' + encoding
                        pass
            except ImportError:
                pass
        return pattern

    def SetPattern(self, pattern):
        self.pattern = pattern

    def GetKind(self):
        return self.kind
    def GetAbbrKind(self):
        return RevCKinds[self.kind]
    def SetKind(self, kind):
        # 保存的类型必须为全名
        if len(kind) == 1:
            kind = CKinds[kind]
        self.kind = kind.strip()

    def GetParent(self):
        return self.parent
    def SetParent(self, parent):
        self.parent = parent

    def GetParentType(self):
        return self.GetExtField('parent_type')
    def SetParentType(self, parentType):
        self.exts['parent_type'] = parentType

    def GetQualifiers(self):
        return self.qualifiers
    def SetQualifiers(self, qualifiers):
        self.qualifiers = qualifiers

    def GetAccess(self):
        return self.GetExtField("access")
    def SetAccess(self, access):
        self.exts["access"] = access

    def GetSignature(self):
        return self.GetExtField("signature")
    def SetSignature(self, sig):
        self.exts["signature"] = sig

    def SetInherits(self, inherits):
        self.exts["inherits"] = inherits
    def GetInherits(self):
        return self.GetInheritsAsString()

    def GetTemplate(self):
        return self.GetExtField("template")
    def SetTemplate(self, template):
        self.exts['template'] = template

    def GetTyperef(self):
        return self.GetExtField("typeref")
    def SetTyperef(self, typeref):
        self.exts["typeref"] = typeref

    def GetInheritsAsString(self):
        return self.GetExtField('inherits')

    def GetInheritsAsArrayNoTemplates(self):
        '''返回清除了模版信息的继承字段的列表'''
        inherits = self.GetInheritsAsString()
        parent = ''
        parentsArr = []

        # 清楚所有尖括号内的字符串
        depth = 0
        for ch in inherits:
            if ch == '<':
                if depth == 0 and parent:
                    parentsArr.append(parent.strip())
                    parent = ''
                depth += 1
            elif ch == '>':
                depth -= 1
            elif ch == ',':
                if depth == 0 and parent:
                    parentsArr.append(parent.strip())
                    parent = ''
            else:
                if depth == 0:
                    parent += ch

        if parent:
            parentsArr.append(parent.strip())

        return parentsArr

    def GetInheritsAsArrayWithTemplates(self):
        inherits = self.GetInheritsAsString()
        parent = ''
        parentsArr = []

        depth = 0
        for ch in inherits:
            if ch == '<':
                depth += 1
                parent += ch
            elif ch == '>':
                depth -= 1
                parent += ch
            elif ch == ',':
                if depth == 0 and parent:
                    parentsArr.append(parent.strip())
                    parent = ''
                elif depth != 0:
                    parent += ch
            else:
                parent += ch

        if parent:
            parentsArr.append(parent.strip())

        return parentsArr

    def GetReturn(self):
        return self.GetExtField('return')
    def SetReturn(self, retVal):
        self.exts["return"] = retVal

    def GetScope(self):
        return self.scope
    def SetScope(self, scope):
        self.scope = scope

    def GetScopeName(self):
        '''Return scope name of the tag.

        If path is empty in db or contains just the project name, 
        it will return the literal <global>.
        For project tags, an empty string is returned.
        '''
        return self.GetScope()

    def Key(self):
        '''Generate a Key for this tag based on its attributes

        Return tag key'''
        # 键值为 [原型/宏:]path:signature
        key = ''
        if self.GetKind() == 'prototype' or self.GetKind() == 'macro':
            key += self.GetKind() + ': '

        key += self.GetPath() + self.GetSignature()
        return key

    def GetDisplayName(self):
        '''Generate a display name for this tag to be used by the symbol tree

        Return tag display name'''
        return self.GetName() + self.GetSignature()

    def GetFullDisplayName(self):
        '''Generate a full display name for this tag that includes:
        full scope + name + signature

        Return tag full display name
        '''
        name = ''
        if self.GetParent() == '<global>':
            name += self.GetDisplayName()
        else:
            name += self.GetParent() + '::' + self.GetName() \
                    + self.GetSignature()
        return name

    def NameFromTyperef(self, templateInitList):
        '''Return the actual name as described in the 'typeref' field

        Return real name or wxEmptyString'''
        #TODO
        pass

    def TypeFromTyperef(self):
        '''Return the actual type as described in the 'typeref' field

        return real name or wxEmptyString'''
        typeref = self.GetTyperef()
        if typeref:
            name = typeref.partition(':')[0]
            return name
        else:
            return ''

    # ------------------------------------------
    #  Extenstion fields
    # ------------------------------------------
    def GetExtField(self, extField):
        if self.exts.has_key(extField):
            return self.exts[extField]
        else:
            return ''

    # ------------------------------------------
    #  Misc
    # ------------------------------------------
    def Print(self):
        '''顺序基本与数据库的一致'''
        print '======================================'
        print 'Name:\t\t' + self.GetName()
        print 'File:\t\t' + self.GetFile()
        print 'Line:\t\t' + str(self.GetLine())
        print 'Text:\t\t' + self.GetText()
        print 'Kind:\t\t' + self.GetKind()
        print 'Parent:\t\t' + self.GetParent()
        print 'Path:\t\t' + self.GetPath()
        print 'Scope:\t\t' + self.GetScope()
        print ' ---- Ext fields: ---- '
        for k, v in self.exts.iteritems():
            print k + ':\t\t' + v
        print '======================================'

    def UpdatePath(self, scope):
        '''Update the path with full path (e.g. namespace::class)'''
        path = ''
        if not scope or scope == '<global>':
            path = ''
        else:
            path = scope
            path += '::'
        path += self.GetName()
        self.SetPath(path)

    def TypedefFromPattern(self, tagPattern, typedefName, name, templateInit):
        '''从 tags 中的 pattern 字段提取 typedef'''
        pattern = tagPattern.lstrip('/^')
        #TODO: 需要 lex...
        pass


if __name__ == '__main__':
    import os.path
    FILE = 'tags2'
    FILE = '/tmp/tags'
    if os.path.exists(FILE):
        with open(FILE) as f:
            for line in f:
                if line.startswith('!'):
                    continue
                print line,
                entry = TagEntry()
                entry.FromLine(line)
                entry.Print()

    print GetMacroSignature('#define MIN(x, y) x < y ? x : y')
    entry = TagEntry()
    lines = [
        'ab\tmain.c\t/^  ab,$/;"\tenumerator\tline:12\tenum:abc\ttext:ab',
        'xy\tmain.c\t/^  int xy;$/;"\tmember\tline:16\tstruct:xyz\taccess:public\ttext:int xy;'
    ]
    for line in lines:
        entry.FromLine(line)
        entry.Print()

