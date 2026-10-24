import ast
from pathlib import Path
root=Path('shell')
catalog=ast.parse((root/'i18n.py').read_text(encoding='utf-8'))
translations=next(ast.literal_eval(n.value) for n in catalog.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='EN' for t in n.targets))
for name in ['main','preferences','system_ui','capture','applications','wallpapers','shortcuts','desktop','tasks']:
 path=root/(name+'.py')
 source=path.read_bytes()
 tree=ast.parse(source)
 offsets=[0]
 for line in source.splitlines(keepends=True): offsets.append(offsets[-1]+len(line))
 changes=[]
 def visit(node):
  if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='tr': return
  matched=isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value in translations
  if isinstance(node,ast.JoinedStr):
   matched=any(isinstance(x,ast.Constant) and x.value in translations for x in node.values)
   if not matched: return
  if matched:
   start=offsets[node.lineno-1]+node.col_offset
   end=offsets[node.end_lineno-1]+node.end_col_offset
   changes.append((start,end,b'tr('+source[start:end]+b')'))
   return
  for child in ast.iter_child_nodes(node): visit(child)
 visit(tree)
 for start,end,value in sorted(changes,reverse=True): source=source[:start]+value+source[end:]
 new=source.decode('utf-8')
 if 'from i18n import tr' not in new:
  position=new.find('\n')+1
  new=new[:position]+'from i18n import tr\n'+new[position:]
 ast.parse(new)
 path.write_text(new,encoding='utf-8',newline='\n')
 print(name,len(changes))
