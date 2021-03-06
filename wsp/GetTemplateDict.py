#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os.path
from VLProject import VLProject
from Misc import DirSaver, IsWindowsOS

def GetTemplateDict(dir):
    ds = DirSaver()
    try:
        os.chdir(dir)
    except:
        return {}

    templates = {}
    for dir in os.listdir(dir):
        projFile = os.path.join(dir, os.path.basename(dir) + '.project')
        if os.path.isdir(dir) and os.path.isfile(projFile):
            tmpProj = VLProject(projFile)
            internalType = tmpProj.GetProjectInternalType()

            template = {}
            template['name'] = tmpProj.GetName()
            template['file'] = tmpProj.GetFileName()
            template['desc'] = tmpProj.GetDescription()
            bldConf = tmpProj.GetSettings().GetBuildConfiguration('Debug')
            template['cmpType'] = bldConf.GetCompilerType()

            if internalType:
                if not templates.has_key(internalType):
                    templates[internalType] = []
                templates[internalType].append(template)
            else:
                if not templates.has_key('Others'):
                    templates['Others'] = []
                templates['Others'].append(template)
    return templates


def test():
    if IsWindowsOS():
        templatesDir = r'D:\Program Files\Vim\vimlite\templates\projects'
    else:
        templatesDir = '/home/eph/.codelite/templates/projects'
    templates = GetTemplateDict(templatesDir)
    for k, v in templates.iteritems():
        print k
        for i in v:
            print i['name']
            print i['file']
            print i['desc']
            print i['cmpType']
            print '-' * 40
        print '-' * 80


if __name__ == '__main__':
    test()

