'''
MAIN script
used for test and builds
'''

import dungeon_gen as Dgen

Dun = Dgen.Dungeon(2, "my dungeon")

print(Dun.rooms[0][0].paths)
print("hello")