import math 
from . import *
from pya import *

class T_SWG_MultiBox_Ring(pya.PCellDeclarationHelper):

    def __init__(self):

      # Important: initialize the super class
      super(T_SWG_MultiBox_Ring, self).__init__()
      TECHNOLOGY = get_technology_by_name('EBeam')

      # declare the parameters
      self.param("pitch", self.TypeDouble, "Period [um]", default = 0.25)
      self.param("w", self.TypeDouble, "Waveguide Width [um]", default = 0.5)
      self.param("r", self.TypeDouble, "Radius [um]", default = 35)
      self.param("ff", self.TypeDouble, "Duty Cycle (Inner Trapezoidal Length)", default = 0.75)
      self.param("outerL", self.TypeDouble, "Outer Trapezoidal Length [um]", default = 0.15)
     
      self.param("doublebus", self.TypeBoolean, "Bus Type (Single=False, Double=True)", default = True)
      self.param("ff2", self.TypeDouble, "Bus Duty Cycle", default = 0.7)
      self.param("busL", self.TypeDouble, "Bus Length [um]", default = 10)

      self.param("angle", self.TypeDouble, "Angle", default = 360)

      self.param("gap", self.TypeDouble, "Row Gap [um]", default = 0.06)
      self.param("gap2", self.TypeDouble, "Bus Gap [um]", default = 0.06)

      self.param("taperL", self.TypeDouble, "Taper Length [um]", default = 25)
      self.param("wtaper", self.TypeDouble, "Taper End Width [um]", default = 0.1)
      self.param("wport", self.TypeDouble, "Waveguide Port Width [um]", default = 0.5)

      self.param("fishbone", self.TypeBoolean, "Fishbone (True for Fishbone)", default = False)
      self.param("fishbone_loc", self.TypeBoolean, "Center (True) or Edge Fishbone (False)", default = True)

      self.param("np", self.TypeInt, "Number of points", default = 2048) 
      self.param("layer", self.TypeLayer, "Layer", default = TECHNOLOGY['Waveguide'])
      self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
      self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
      self.param("oxideopen", self.TypeLayer, "Oxide Open Layer", default = TECHNOLOGY['Oxide open (to BOX)'])

    # Calculate the central axis of datapoints stored in y (for a rectangle or trapezoid)
    def calculate_centroid(self, y):
      return (y[1] + y[2])/2

    # Creating the layout
    def produce_impl(self):
      from SiEPIC._globals import PIN_LENGTH
      from SiEPIC.extend import to_itype
      import math
      from pya import DPolygon
 
      pi  = math.pi

      # fetch the parameters
      dbu = self.layout.dbu
      ly = self.layout
      shapes = self.cell.shapes
      LayerSi = self.layer
      LayerSiN = ly.layer(LayerSi)
      LayerPinRecN = ly.layer(self.pinrec)
      LayerDevRecN = ly.layer(self.devrec)

      #variables
      pitch = self.pitch
      w = self.w
      r = self.r
      ff = self.ff
      ff2 = self.ff2
      iL = pitch*ff
      oL = self.outerL
      angle = self.angle
      gap = self.gap
      gap2 = self.gap2
      busL = self.busL
      taperL = self.taperL
      wport = self.wport
      wtaper = self.wtaper
      fishbone = self.fishbone
      fishbone_loc = self.fishbone_loc
      doublebus = self.doublebus
      
      
      if (r-w/2 <= 0):
        r = 5
        print ('invalid radius, set r to default: 5')
      if busL <= 10:
        busL = taperL*2+10
        print('invalid length of SWG bus waveguide, set length at least 2 times larger than taper length and pluse 10 um')
      
      #Calculate number of segments
      s1 = pitch*ff #silicon
      s2 = pitch-s1 #gap

      # draw oxide open 
      shapes(ly.layer(self.oxideopen)).insert(
        pya.Box(
            DPoint(-to_itype(r+5,dbu),-to_itype(r+5,dbu)),
            DPoint(to_itype(r+5,dbu),to_itype(r+5,dbu)) ) )
      
      # Draw the Multi-box Ring
      first_grating = True
      
      for i in range(1): # draw different radius SWG rings
        
        #calculate best radius
        const = math.floor(2*pi*r/(s1+s2))
        
        #if doesn't divide evenly, replace r with best possible r
        if ((2*pi*r)%(s1+s2) != 0):
          r = const*(s1+s2)/(2*pi)
          print('r adjusted to '+str(r)+'um to fit periods perfectly.')
        
        theta1 = math.atan(s1/r)
        theta2 = math.atan(s2/r)
        nSeg = int(math.floor(angle/(math.degrees(theta1)+math.degrees(theta2)))) #how many segments to have
        
        si_first = True #for alternating between silicon and gap
        j = 0 #index of how many silicon thetas 
        jj = 0 #index of how many gap thetas
        ORDER = True #ordering of the coordinates for polygon drawing
        dtheta = math.atan((oL-iL)/(2*r))

        xo_ring = [(r-w/2)*math.cos(0)]
        yo_ring = [(r-w/2)*math.sin(0)]
        xo_ring.append((r+w/2)*math.cos(0-dtheta))
        yo_ring.append((r+w/2)*math.sin(0-dtheta))

        for i in range(0,nSeg*2):
            if si_first:
                j = j+1
                si_first = not(si_first)
            else:
                jj=jj+1
                si_first = not(si_first)
            
            if ORDER: 
              xo_ring.append((r+w/2)*math.cos(j*theta1+jj*theta2+dtheta))
              yo_ring.append((r+w/2)*math.sin(j*theta1+jj*theta2+dtheta))
              xo_ring.append((r-w/2)*math.cos(j*theta1+jj*theta2))
              yo_ring.append((r-w/2)*math.sin(j*theta1+jj*theta2))
              ORDER = not(ORDER)
            else:
              xo_ring.append((r-w/2)*math.cos(j*theta1+jj*theta2))
              yo_ring.append((r-w/2)*math.sin(j*theta1+jj*theta2))
              xo_ring.append((r+w/2)*math.cos(j*theta1+jj*theta2-dtheta))
              yo_ring.append((r+w/2)*math.sin(j*theta1+jj*theta2-dtheta))
              ORDER = not(ORDER)    

            # Ready to make a shape from the points above
            if len(xo_ring) == 4:
              dpts=[pya.DPoint(xo_ring[i], yo_ring[i]) for i in range(len(xo_ring))]
              dpolygon = DPolygon(dpts)
              element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
              shapes(LayerSiN).insert(element)
              
              # computing the central axis of the first grating
              if (first_grating):
                ring_axis = self.calculate_centroid(yo_ring)
                first_grating = False

              # Axis for the doublebus waveguide
              elif (i == nSeg - 1) and (doublebus):
                ring_axis_left = self.calculate_centroid(yo_ring)

              xo_ring = []
              yo_ring = [] 
        
        # Create a fishbone
        if (fishbone):
          
          w2 = wtaper/dbu
          r2 = r/dbu
          w_in = 0 # w_in is updated when the fishbone is moved toward the inner edge

          # Move fishbone to the inner edge
          if (fishbone_loc == False):
            w_in = w/dbu 
          
          da2 = angle*pi/(180*self.np) # angle increment
          
          # points for the inner and outer rings
          pts_o = []
          pts_i = []
            
          for i in range(0,self.np + 1):
            bend_ox = (r2+(w2)/2 - 0.4*w_in)*math.cos(i*da2)
            bend_oy = (r2+(w2)/2 - 0.4*w_in)*math.sin(i*da2)
            bend_ix = (r2-(w2)/2 - 0.4*w_in)*math.cos(i*da2)
            bend_iy = (r2-(w2)/2 - 0.4*w_in)*math.sin(i*da2)
            pts_o.append(pya.Point.from_dpoint(pya.DPoint(bend_ox,bend_oy)))
            pts_i.append(pya.Point.from_dpoint(pya.DPoint(bend_ix,bend_iy)))
          
          pts_o.append(pya.Point.from_dpoint(pya.DPoint(0,r2+w2/2 - 0.4*w_in)))
          pts_i.append(pya.Point.from_dpoint(pya.DPoint(0,r2-w2/2 - 0.4*w_in)))
          pts_o.append(pya.Point.from_dpoint(pya.DPoint(0,0)))
          pts_i.append(pya.Point.from_dpoint(pya.DPoint(0,0)))

          ring1 = pya.Region()
          ring1.insert(pya.Polygon(pts_o))
          ring2 = pya.Region()
          ring2.insert(pya.Polygon(pts_i))
          ring = ring1-ring2
          shapes(LayerSiN).insert(ring)
          
        r = r - (w+gap) 
      
        
      ##### BUS WAVEGUIDE ONE:  
      # Draw the Bus Waveguides 
        
      s1 = pitch*ff2#silicon
      s2 = pitch-s1 #gap
      r = self.r # original (non-adjusted) r

      #if doesn't divide evenly, replace r with best possible r
      if ((2*pi*r)%(s1+s2) != 0):
          const = math.floor(2*pi*r/(s1+s2)) # factor for reshaping the radius if needed
          r = const*(s1+s2)/(2*pi)
      
      # calulate ideal length of bus
      bus_length = busL
      constant = math.ceil(bus_length/(s1+s2))
      if bus_length % (s1 + s2) != 0:
        bus_length = constant*(s1+s2)
        
      for ii in range(1):
        
        # the middle SWG
        xo = [(r+w/2+gap2+ii*(w+gap)),(r+w/2+gap2+w+ii*(w+gap)),(r+w/2+gap2+w+ii*(w+gap)),(r+w/2+gap2+ii*(w+gap))]
        yo = [0, 0, s1, s1]
        
        # Checking for bus symmetry 
        bus_axis = self.calculate_centroid(yo)
        diff_axis = bus_axis - ring_axis
 
        # SWG is above the bus, shift the bus upward
        if (diff_axis < -0.0001):
          while (diff_axis < -0.0001):
            yo = [yo[0] + 0.0001, yo[1] + 0.0001, yo[2] + 0.0001, yo[3] + 0.0001]
            bus_axis = self.calculate_centroid(yo)
            diff_axis = bus_axis - ring_axis

        # SWG is below the bus, shift the bus down
        elif (diff_axis > 0.0001 ):
          while (diff_axis >= 0.0001):
            yo = [yo[0] - 0.0001, yo[1] - 0.0001, yo[2] - 0.0001, yo[3] - 0.0001]
            bus_axis = self.calculate_centroid(yo)
            diff_axis = bus_axis - ring_axis
        
        dpts=[pya.DPoint(xo[i], yo[i]) for i in range(len(xo))]
        dpolygon = DPolygon(dpts)
        element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
        shapes(LayerSiN).insert(element)

        n = int(math.ceil((constant)/2)) # SWG Gratings (before the taper) above and below the central grating (minus one)  
        for i in range(n):
          yu = [yo[j] + i*pitch for j in range(len(yo))] # n-1 SWG's above the middle SWG
          yd = [yo[j] - i*pitch for j in range(len(yo))] # n-1 SWG below the middle SWG
            
          dpts = [pya.DPoint(xo[i], yu[i]) for i in range(len(xo))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element)
          dpts = [pya.DPoint(xo[i], yd[i]) for i in range(len(xo))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element) 
        
        # Top taper in the SWG
        xtu = [((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2),((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2+wtaper),((r+w/2+gap2+ii*(w+gap))+w+gap/2),((r+w/2+gap2+ii*(w+gap))-gap/2)]
        ytu = [(yu[3]-taperL),(yu[3]-taperL),(yu[3]),(yu[3])]
        dpts=[pya.DPoint(xtu[i], ytu[i]) for i in range(len(xtu))]
        dpolygon = DPolygon(dpts)
        element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
        shapes(LayerSiN).insert(element)
        
        # Bottom tapers in the SWG
        ytd = [(yd[1]+taperL),(yd[1]+taperL),(yd[1]),(yd[1])]
        dpts=[pya.DPoint(xtu[i], ytd[i]) for i in range(len(xtu))]
        dpolygon = DPolygon(dpts)
        element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
        shapes(LayerSiN).insert(element)
      
        # Adding the fishbone
        if (fishbone):
          xstd = [((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2),((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2+wtaper),((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2+wtaper),((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2)]
          ystd = [(yu[3]-taperL),(yu[3]-taperL),(yd[1]+taperL),(yd[1]+taperL)]
          dpts=[pya.DPoint(xstd[i], ystd[i]) for i in range(len(xstd))]
          dpolygon = DPolygon(dpts)
          element2 = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element2)  
        
      # Adding the top standard waveguide
      xTu = [(r+w/2+gap2-gap/2),(r+w/2+gap2-gap/2+(gap+w)),(r+w/2+gap2+(gap+w)/2+wport/2),(r+w/2+gap2+(gap+w)/2-wport/2)]
      yTu = [(yu[3]),(yu[3]),(yu[3]+taperL),(yu[3]+taperL)]
      dpts=[pya.DPoint(xTu[i], yTu[i]) for i in range(len(xTu))]
      dpolygon = DPolygon(dpts)
      element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
      shapes(LayerSiN).insert(element) 
      
      # Adding the bottom standard waveguide
      yTd = [(yd[1]),(yd[1]),(yd[1]-taperL),(yd[1]-taperL)]
      dpts=[pya.DPoint(xTu[i], yTd[i]) for i in range(len(xTu))]
      dpolygon = DPolygon(dpts)
      element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
      shapes(LayerSiN).insert(element) 
      
      # add std WG - Not Called
      if 2*r >= busL + 2*taperL:
        xstdu = [(r+w/2+gap2+(gap+w)/2  - wport/2),(r+w/2+gap2+(gap+w)/2  + wport/2),(r+w/2+gap2+(gap+w)/2 + wport/2),(r+w/2+gap2+(gap+w)/2 - wport/2)]
        ystdu = [(yu[3]+taperL),(yu[3]+taperL),(yu[3]+r-busL/2+1),(yu[3]+r-busL/2+1)]
        dpts=[pya.DPoint(xstdu[i], ystdu[i]) for i in range(len(xstdu))]
        dpolygon = DPolygon(dpts)
        element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
        shapes(LayerSiN).insert(element)  
        
        ystdd = [(yd[1]-taperL),(yd[1]-taperL),(yd[1]-r+busL/2-1),(yd[1]-r+busL/2-1)]
        dpts=[pya.DPoint(xstdu[i], ystdd[i]) for i in range(len(xstdu))]
        dpolygon = DPolygon(dpts)
        element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
        shapes(LayerSiN).insert(element) 
      
      else:
        xstdu = xTu 
        ystdu = yTu 
        ystdd = yTd 

      # Storing temp wg width, bus length, and gap because they are modified in the DEV BOX
      # These are used if a drop waveguide is used
      w_temp = w
      bus_length_temp = bus_length
      gap_temp = gap

      #DEV BOX
      half_l = (self.cell.bbox().width()-(gap+w)/dbu-gap2/dbu+(gap/2)/dbu)/2
      half_r = self.cell.bbox().width()-half_l
      dev = Box(-half_l,ystdd[-1]/dbu,half_r,ystdu[-1]/dbu)
      shapes(LayerDevRecN).insert(dev)
      dev_width = self.cell.bbox().width()/2
      
      if 2*r >= busL + 2*taperL:
        dev_up = yu[-1]/dbu +taperL/dbu +(yu[3]+r-busL/2 +1-(yu[3]+taperL))/dbu
        dev_down = yd[-4]/dbu - taperL/dbu - (yu[3]+r-busL/2 +1 -(yu[3]+taperL))/dbu
      else:
        dev_up = yu[-1]/dbu + taperL/dbu 
        dev_down = yd[-4]/dbu - taperL/dbu

      # Create the pins on the waveguides, as short paths:
      from SiEPIC._globals import PIN_LENGTH as pin_length
      
      w = to_itype(self.w,dbu)
      gap = to_itype(self.gap,dbu)
      bus_length = to_itype(bus_length/2,dbu)

      #Pin1
      t = Trans(Trans.R0, xstdu[-1]/dbu+wport/2*1000+1,dev_up)
      pin = Path([Point(0, -pin_length/2), Point(0, pin_length/2)], wport*1000) #500 is width of std WG
      pin_t = pin.transformed(t)
      shapes(LayerPinRecN).insert(pin_t)
      text = Text ("opt1", t)
      shape = shapes(LayerPinRecN).insert(text)
      shape.text_size = 0.4/dbu

      #Pin2
      t = Trans(Trans.R0, xstdu[-1]/dbu+wport/2*1000+1,dev_down)
      pin = Path([Point(0, pin_length/2), Point(0, -pin_length/2)], wport*1000)
      pin_t = pin.transformed(t)
      shapes(LayerPinRecN).insert(pin_t)
      text = Text ("opt2", t)
      shape = shapes(LayerPinRecN).insert(text)
      shape.text_size = 0.4/dbu

      
      #DROP WAVEGUIDE:  
      if (doublebus):
        # Reinitializing the values that were modified in the DEV-BOX
        w = w_temp
        bus_length = bus_length_temp
        gap = gap_temp
        
        s1 = pitch*ff2 #silicon
        s2 = pitch-s1 #gap

        r = self.r
        const = math.floor(2*pi*r/(s1+s2))

        #if doesn't divide evenly, replace r with best possible r
        if ((2*pi*r)%(s1+s2) != 0):
            r = const*(s1+s2)/(2*pi)
        
        #calulate ideal length of bus
        bus_length = busL
        #bus_length = self.cell.bbox().height()*dbu +pitch*2
        constant = math.ceil(bus_length/(s1+s2))
        if bus_length % (s1+s2) != 0:
          bus_length = constant*(s1+s2)
          
        for ii in range(1):
          
          # the middle SWG
          xo = [-(r+w/2+gap2+ii*(w+gap)),-(r+w/2+gap2+w+ii*(w+gap)),-(r+w/2+gap2+w+ii*(w+gap)),-(r+w/2+gap2+ii*(w+gap))]
          yo = [0,0,s1,s1]
          
          # Checking for bus symmetry 
          bus_axis = self.calculate_centroid(yo)
          diff_axis = bus_axis - ring_axis_left
  
          # SWG is above the bus, shift the bus upward
          if (diff_axis < -0.0001):
            while (diff_axis < -0.0001):
              yo = [yo[0] + 0.0001, yo[1] + 0.0001, yo[2] + 0.0001, yo[3] + 0.0001]
              bus_axis = self.calculate_centroid(yo)
              diff_axis = bus_axis - ring_axis_left

          # SWG is below the bus, shift the bus down
          elif (diff_axis > 0.0001 ):
            while (diff_axis > 0.0001):
              yo = [yo[0] - 0.0001, yo[1] - 0.0001, yo[2] - 0.0001, yo[3] - 0.0001]
              bus_axis = self.calculate_centroid(yo)
              diff_axis = bus_axis - ring_axis_left
          
          dpts=[pya.DPoint(xo[i], yo[i]) for i in range(len(xo))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element)

          n = int(math.ceil((constant)/2)) # SWG Gratings (before the taper) above and below the central grating (minus one)  
          for i in range(n):
            yu = [yo[j] + i*pitch for j in range(len(yo))] # n-1 SWG's above the middle SWG
            yd = [yo[j] - i*pitch for j in range(len(yo))] # n-1 SWG below the middle SWG
              
            dpts = [pya.DPoint(xo[i], yu[i]) for i in range(len(xo))]
            dpolygon = DPolygon(dpts)
            element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
            shapes(LayerSiN).insert(element)
            dpts = [pya.DPoint(xo[i], yd[i]) for i in range(len(xo))]
            dpolygon = DPolygon(dpts)
            element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
            shapes(LayerSiN).insert(element) 
          
          # draw the tapers from waveguide to SWG
          xtu = [-((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2),-((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2+wtaper),-((r+w/2+gap2+ii*(w+gap))+w+gap/2),-((r+w/2+gap2+ii*(w+gap))-gap/2)]
          ytu = [(yu[3]-taperL),(yu[3]-taperL),(yu[3]),(yu[3])]
          dpts=[pya.DPoint(xtu[i], ytu[i]) for i in range(len(xtu))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element)
          
          ytd = [(yd[1]+taperL),(yd[1]+taperL),(yd[1]),(yd[1])]
          dpts=[pya.DPoint(xtu[i], ytd[i]) for i in range(len(xtu))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element)

          # Add the fishbone 
          if (fishbone):
            xstd = [-((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2),-((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2+wtaper),-((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2+wtaper),-((r+w/2+gap2+ii*(w+gap))+(w-wtaper)/2)]
            ystd = [(yu[3]-taperL),(yu[3]-taperL),(yd[1]+taperL),(yd[1]+taperL)]
            dpts=[pya.DPoint(xstd[i], ystd[i]) for i in range(len(xstd))]
            dpolygon = DPolygon(dpts)
            element2 = Polygon.from_dpoly(dpolygon*(1.0/dbu))
            shapes(LayerSiN).insert(element2)  
          
        # taper connections from multi-tapers to std WG
        xTu = [-(r+w/2+gap2-gap/2),-(r+w/2+gap2-gap/2+(gap+w)),-(r+w/2+gap2+(gap+w)/2+wport/2),-(r+w/2+gap2+(gap+w)/2-wport/2)]
        yTu = [(yu[3]),(yu[3]),(yu[3]+taperL),(yu[3]+taperL)]
        dpts=[pya.DPoint(xTu[i], yTu[i]) for i in range(len(xTu))]
        dpolygon = DPolygon(dpts)
        element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
        shapes(LayerSiN).insert(element) 
        yTd = [(yd[1]),(yd[1]),(yd[1]-taperL),(yd[1]-taperL)]
        dpts=[pya.DPoint(xTu[i], yTd[i]) for i in range(len(xTu))]
        dpolygon = DPolygon(dpts)
        element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
        shapes(LayerSiN).insert(element) 
        
        # add std WG - Not Called
        if 2*r >= busL + 2*taperL:
          xstdu = [-(r+w/2+gap2+(gap+w)/2  - wport/2),-(r+w/2+gap2+(gap+w)/2  + wport/2),-(r+w/2+gap2+(gap+w)/2 + wport/2),-(r+w/2+gap2+(gap+w)/2 - wport/2)]
          ystdu = [(yu[3]+taperL),(yu[3]+taperL),(yu[3]+r-busL/2+1),(yu[3]+r-busL/2+1)]
          dpts=[pya.DPoint(xstdu[i], ystdu[i]) for i in range(len(xstdu))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element)  
          
          ystdd = [(yd[1]-taperL),(yd[1]-taperL),(yd[1]-r+busL/2-1),(yd[1]-r+busL/2-1)]
          dpts=[pya.DPoint(xstdu[i], ystdd[i]) for i in range(len(xstdu))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element) 
        else:
          xstdu = xTu 
          ystdu = yTu 
          ystdd = yTd 

        # Create the pins on the waveguides, as short paths:
        #from SiEPIC._globals import PIN_LENGTH as pin_length
    
        w = to_itype(self.w,dbu)
        gap = to_itype(self.gap,dbu)
        bus_length = to_itype(bus_length/2,dbu)

      
        if 2*r >= busL + 2*taperL:
          dev_up = yu[-1]/dbu +taperL/dbu +(yu[3]+r-busL/2 +1-(yu[3]+taperL))/dbu
          dev_down = yd[-4]/dbu - taperL/dbu - (yu[3]+r-busL/2 +1 -(yu[3]+taperL))/dbu
        else:
          dev_up = yu[-1]/dbu + taperL/dbu 
          dev_down = yd[-4]/dbu - taperL/dbu

        #Pin1
        t = Trans(Trans.R0, xstdu[1]/dbu+wport/2*1000+1,dev_up)
        pin = Path([Point(0, -pin_length/2), Point(0, pin_length/2)], wport*1000) #500 is width of std WG
        pin_t = pin.transformed(t)
        shapes(LayerPinRecN).insert(pin_t)
        text = Text ("opt1", t)
        shape = shapes(LayerPinRecN).insert(text)
        shape.text_size = 0.4/dbu

        #Pin2
        t = Trans(Trans.R0, xstdu[1]/dbu+wport/2*1000+1,dev_down)
        pin = Path([Point(0, pin_length/2), Point(0, -pin_length/2)], wport*1000)
        pin_t = pin.transformed(t)
        shapes(LayerPinRecN).insert(pin_t)
        text = Text ("opt2", t)
        shape = shapes(LayerPinRecN).insert(text)
        shape.text_size = 0.4/dbu