import pstats
p=pstats.Stats('profile.txt')
#p.sort_stats('calls').print_stats()
p.sort_stats('cumulative').reverse_order().print_stats()
