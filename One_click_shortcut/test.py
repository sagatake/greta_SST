import os

files = os.listdir('./')
print(files)

for file in files:
    
    if '.bat' == file[-4:]:
        pass
    else:
        continue
    print(file)
    with open(file, 'r') as f:
        text = f.read()
        print(text)
    
    # print('before: ', text)
    
    # text = text.replace('call cd.bat', 'call src/cd.bat')
    
    # print('after: ', text)
    # # input()
    
    file = file.replace('RolePlay_', '')
    
    with open(file, 'w') as f:
        f.write(text)