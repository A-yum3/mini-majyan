from tile import *

dora = Tile('souzu', '5')

green = [Tile('souzu', '2'), Tile('souzu', '2'), Tile('souzu', '3'), Tile('souzu', '3'),
         Tile('souzu', '4'), Tile('souzu', '4')]

green_1 = [Tile('souzu', '2'), Tile('souzu', '3'), Tile('souzu', '4'),
           Tile('tsangenpai', '10'), Tile('tsangenpai', '10'), Tile('tsangenpai', '10')]

t_yao = [Tile('souzu', '2'), Tile('souzu', '3'), Tile('souzu', '4'), Tile('akazu', '2'), Tile('akazu', '3'),
         Tile('akazu', '4')]

t_yan = [Tile('souzu', '1'), Tile('souzu', '2'), Tile(
    'souzu', '3'), Tile('akazu', '7'), Tile('akazu', '8'), Tile('akazu', '9')]

ti_yao = [Tile('souzu', '1'), Tile('souzu', '1'), Tile('souzu', '1'),
          Tile('souzu', '9'), Tile('souzu', '9'), Tile('souzu', '9')]

su_red = [Tile('akazu', '1'), Tile('akazu', '2'), Tile('akazu', '3'),
          Tile('akazu', '7'), Tile('akazu', '7'), Tile('akazu', '7')]

print(judge(green, dora))
print(judge(green_1, dora))
print(judge(t_yao, dora))
print(judge(t_yan, dora))
print(judge(ti_yao, dora))
print(judge(su_red, dora))
