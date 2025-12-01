

from Ups import Ups




class redundancyN:


    def __init__(self, ups_fr, ups_bc, ups_sp, ups_e, ups_cr):
        
        self.ups = Ups(ups_fr, ups_bc, ups_sp, ups_e, ups_cr, 0)

    def stepHour(self, load, utility):
        self.ups.step(load, utility)
        
