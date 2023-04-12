import pya
from pya import *
from SiEPIC.utils import get_technology_by_name
from SiEPIC._globals import PIN_LENGTH as pin_length
from SiEPIC.extend import to_itype
from pya import DPolygon

import math

class Trapezoidal_SWG_Ring(pya.PCellDeclarationHelper):

    """ 
    
    Author: Ben Cohen (UBC)

       - This PCell creates Trapezoidal-SWG (or rectangular SWG) Ring Resonators with one or two busses
       - The inner and outer lengths can be adjusted by changing the inner/outer ff (fill factor or duty cycle)
       - The PCell provides the option for coupling to one or two busses with a selected coupling gap. Both busses have adjustable tapers from strip inputs to the SWG
       - The SWG and bus can optionally support fishbones. In the ring, the fishbone can be shifted to the inner/outer radius of the ring or simply kept in the middle
    
    """
    def __init__(self):

      # Important: initialize the super class
      super(Trapezoidal_SWG_Ring, self).__init__()
      TECHNOLOGY = get_technology_by_name('EBeam')

      # declare the parameters
      self.param("p", self.TypeDouble, "Period [um]", default = 0.25)
      self.param("w", self.TypeDouble, "Waveguide Width [um]", default = 0.5)
      self.param("r", self.TypeDouble, "Radius [um]", default = 20)
      self.param("ff", self.TypeDouble, "Inner Duty Cycle (period*ff = Inner Trapezoidal Length)", default = 0.5)
      self.param("ffout", self.TypeDouble, "Outer Duty Cycle (period*ff = Outer Trapezoidal Length)", default = 0.5)
      self.param("fishbone", self.TypeBoolean, "Fishbone (True for Fishbone)", default = False)
      self.param("fishbone_loc", self.TypeDouble, "Center Fishbone (0), Inner (1), Outer (2)", default = 0)
      self.param("wfb", self.TypeDouble, "Fishbone Width [um]", default = 0.1)

      self.param("cg", self.TypeDouble, "Coupling Gap [um]", default = 0.5)
      self.param("num_busses", self.TypeDouble, "Number of busses (0, 1, 2)", default = 1)
      self.param("busL", self.TypeDouble, "Bus Length [um]", default = 45)
      self.param("busfb", self.TypeBoolean, "Bus fishbone (True for fishbone)", default = True)
      self.param("ff2", self.TypeDouble, "Bus Fishbone Duty Cycle", default = 0.5)

      self.param("taperL", self.TypeDouble, "Taper Length [um]", default = 15)
      self.param("wport", self.TypeDouble, "Waveguide Port Width [um]", default = 0.5)
      
      self.param("silayer", self.TypeLayer, "Layer", default = TECHNOLOGY['Waveguide'])
      self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
      self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])

    # Calculate the central axis of datapoints stored in y (for a rectangle or trapezoid)
    def calculate_centroid(self, y):
      return (y[0] + y[1])/2

    def calculate_centroid_bus(self, y):
      return (y[1] + y[2])/2

    # Creating the layout
    def produce_impl(self):
      
      pi  = math.pi
    
      # fetch the parameters
      dbu = self.layout.dbu
      ly = self.layout
      shapes = self.cell.shapes
      ly = self.layout

      LayerSiN = ly.layer(self.silayer)
      LayerPinRecN = ly.layer(self.pinrec)
      LayerDevRecN = ly.layer(self.devrec)
      
      np = 2048                         # Number of points for building the ring

      #variables
      p = self.p                        # Grating period [um]
      w = self.w                        # Waveguide Width [um]
      r = self.r                        # Ring radius [um]
      ff = self.ff                      # Duty cycle, p*ff = inner length of grating
      ffout = self.ffout                # SWG outer duty cycle
      oL = p*ffout                        # SWG outer length [um]
      iL = p*ff                         # SWG inner length [um]
      fishbone = self.fishbone          # Fishbone (true), no fishbone (false)
      fishbone_loc = self.fishbone_loc  # Fishbone location (0 = center, 1 = inner edge, 2 = outer edge)      
      w_fb = self.wfb                   # Taper final width [um]
      cg = self.cg                      # Coupling gap [um]
      num_busses = self.num_busses      # Number of busses
      busL = self.busL                  # Bus length [um]
      busfb = self.busfb                # bus fishbone
      ff2 = self.ff2                    # Bus duty cycle      
      taperL = self.taperL              # Taper length [um]
      wport = self.wport                # Strip port width [um]


      s1 = p*ff   # silicon
      s2 = p - s1 # gap

      const = math.floor(2*pi*r/(s1 + s2)) # calculate best radius
      #if doesn't divide evenly, replace r with best possible r to fit the desired number of segments
      if ((2*pi*r)%(s1 + s2) != 0):
        r = const*(s1 + s2)/(2*pi)

      #####################################
      ############# SWG Ring #############
      ###################################
      nSeg =  math.ceil(2 * math.pi * r /p) # Number of segments
      angle_increment = 2 * math.pi / (nSeg + 6) # Angle increment in the SWG along the circumference
      nSeg += 6

      rect_height = 2*w # Rectangle height

      # Drawing the SWG's projected along a circle with radius r
      counter = 0
      for i in range(nSeg):
        theta = i * angle_increment # angle of the rectangle

        x = r * math.cos(theta)
        y = r * math.sin(theta)
        dx = iL / 2
        dy = rect_height / 2

        # x and y coordinates of the SWG gratings - rectangular
        xo_ring = [x - dx * math.cos(theta - math.pi/2) + dy * math.cos(theta), 
                  x - dx * math.cos(theta + math.pi/2) + dy * math.cos(theta),
                  x + dx * math.cos(theta - math.pi/2),
                  x + dx * math.cos(theta + math.pi/2)
                  ]
        
        yo_ring = [y - dx * math.sin(theta - math.pi/2) + dy * math.sin(theta),
                  y - dx * math.sin(theta + math.pi/2) + dy * math.sin(theta),
                  y + dx * math.sin(theta - math.pi/2),
                  y + dx * math.sin(theta + math.pi/2)
                  ]
        
        # Adapting the rectangular gratings to trapezoids!
        if (xo_ring[0] == xo_ring[1]):
            if counter == 0:
              yo_ring[0] = yo_ring[0] + (oL - iL)/2
              yo_ring[1] = yo_ring[1] - (oL - iL)/2
              counter += 1
            else:
              yo_ring[0] = yo_ring[0] - (oL - iL)/2
              yo_ring[1] = yo_ring[1] + (oL - iL)/2
              
        else:
            m = (yo_ring[0] - yo_ring[1])/(xo_ring[0] - xo_ring[1]) # slope of the rectangle
            dt = math.atan(m) # inverse angle
            if (theta < pi):
                xo_ring[1] = xo_ring[1] + (oL - iL)/2*math.cos(dt)
                yo_ring[1] = yo_ring[1] + (oL - iL)/2*math.sin(dt)

                xo_ring[0] = xo_ring[0] - (oL - iL)/2*math.cos(dt)
                yo_ring[0] = yo_ring[0] - (oL - iL)/2*math.sin(dt)
            
            else:
                xo_ring[1] = xo_ring[1] - (oL - iL)/2*math.cos(dt)
                yo_ring[1] = yo_ring[1] - (oL - iL)/2*math.sin(dt)

                xo_ring[0] = xo_ring[0] + (oL - iL)/2*math.cos(dt)
                yo_ring[0] = yo_ring[0] + (oL - iL)/2*math.sin(dt)


        dpts = [pya.DPoint(xo_ring[i], yo_ring[i]) for i in range(len(xo_ring))]
        dpolygon = DPolygon(dpts)
        element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
        shapes(LayerSiN).insert(element)
        
        # computing the central axis of the first grating
        if (i == 0):
          ring_axis = self.calculate_centroid(yo_ring)

        # Axis for the doublebus waveguide
        elif (i == nSeg - 1 or i == nSeg) and (num_busses > 1):
          ring_axis_left = self.calculate_centroid(yo_ring)
      
      # SWG Fishbone
      if (fishbone):
        
        w_wg = w/dbu
        wfb_i = w_fb/dbu
        r2 = r/dbu
        w_in = 0 # w_in is updated when the fishbone is moved toward the inner/outer edges

        # Move fishbone to the inner edge
        if (fishbone_loc == 1):
          w_in = -(w_wg - wfb_i)/2

        # Move fishbone to the outer edge
        elif (fishbone_loc == 2):
          w_in = (w_wg - wfb_i)/2
        
        # points for the inner and outer rings
        pts_o = []
        pts_i = []
        
        da2 = 360*pi/(180*np) # angle increment

        for i in range(0, np + 1):
          bend_ox = (r2 + w_wg/2 + wfb_i/2 + w_in)*math.cos(i*da2)
          bend_oy = (r2 + w_wg/2 + wfb_i/2 + w_in)*math.sin(i*da2)
          bend_ix = (r2 + w_wg/2 - wfb_i/2 + w_in)*math.cos(i*da2)
          bend_iy = (r2 + w_wg/2 - wfb_i/2 + w_in)*math.sin(i*da2)
          pts_o.append(pya.Point.from_dpoint(pya.DPoint(bend_ox, bend_oy)))
          pts_i.append(pya.Point.from_dpoint(pya.DPoint(bend_ix, bend_iy)))
        
        pts_o.append(pya.Point.from_dpoint(pya.DPoint(0, r2 + w_wg/2 + wfb_i/2 + w_in)))
        pts_i.append(pya.Point.from_dpoint(pya.DPoint(0, r2 + w_wg/2 - wfb_i/2 + w_in)))
        pts_o.append(pya.Point.from_dpoint(pya.DPoint(0, 0)))
        pts_i.append(pya.Point.from_dpoint(pya.DPoint(0, 0)))

        ring1 = pya.Region()
        ring1.insert(pya.Polygon(pts_o))
        ring2 = pya.Region()
        ring2.insert(pya.Polygon(pts_i))
        ring = ring1-ring2
        shapes(LayerSiN).insert(ring)
              
      #####################################
      ############# Bus Wg 1 #############
      ###################################
      if (num_busses > 0):
        s1 = p*ff2  #silicon
        s2 = p - s1 #gap
        r = self.r  # original (non-adjusted) r

        #if doesn't divide evenly, replace r with best possible r
        if ((2*pi*r)%(s1 + s2) != 0):
            const = math.floor(2*pi*r/(s1 + s2)) # factor for reshaping the radius if needed
            r = const*(s1 + s2)/(2*pi)
        
        # calulate ideal length of bus
        bus_length = busL
        constant = math.ceil(2*taperL/(s1 + s2))
          
        for ii in range(1):
          
          # the middle SWG
          xo = [r + w + cg + ii*w,
                r + w + cg + w + ii*w,
                r + w + cg + w + ii*w,
                r + w + cg + ii*w]
          
          yo = [0, 0, s1, s1]

          # Checking for bus symmetry 
          bus_axis = self.calculate_centroid_bus(yo)
          diff_axis = bus_axis - ring_axis
  
          # SWG is above the bus, shift the bus upward
          if (diff_axis < -0.0001):
            while (diff_axis < -0.0001):
              yo = [yo[0] + 0.0001, yo[1] + 0.0001, yo[2] + 0.0001, yo[3] + 0.0001]
              bus_axis = self.calculate_centroid_bus(yo)
              diff_axis = bus_axis - ring_axis

          # SWG is below the bus, shift the bus down
          elif (diff_axis > 0.0001 ):
            while (diff_axis >= 0.0001):
              yo = [yo[0] - 0.0001, yo[1] - 0.0001, yo[2] - 0.0001, yo[3] - 0.0001]
              bus_axis = self.calculate_centroid_bus(yo)
              diff_axis = bus_axis - ring_axis
          
          dpts = [pya.DPoint(xo[i], yo[i]) for i in range(len(xo))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element)

          n = int(math.ceil((constant))) # number of SWG Gratings (before the taper) above and below the central grating (minus one)  
          for i in range(n):
            yu = [yo[j] + i*p for j in range(len(yo))] # n-1 SWG's above the middle SWG
            yd = [yo[j] - i*p for j in range(len(yo))] # n-1 SWG below the middle SWG
              
            dpts = [pya.DPoint(xo[i], yu[i]) for i in range(len(xo))]
            dpolygon = DPolygon(dpts)
            element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
            shapes(LayerSiN).insert(element)
            dpts = [pya.DPoint(xo[i], yd[i]) for i in range(len(xo))]
            dpolygon = DPolygon(dpts)
            element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
            shapes(LayerSiN).insert(element) 
          
          # Top taper in the SWG
          xtu = [r + w + cg + ii*w + (w - w_fb)/2,
                 r + w + cg + ii*w + (w - w_fb)/2 + w_fb,
                 r + w + cg + ii*w + w,
                 r + w + cg + ii*w]

          ytu = [yu[3] - taperL, 
                 yu[3] - taperL, 
                 yu[3], 
                 yu[3]]

          dpts = [pya.DPoint(xtu[i], ytu[i]) for i in range(len(xtu))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element)
          
          # Bottom tapers in the SWG
          ytd = [yd[1] + taperL, 
                 yd[1] + taperL, 
                 yd[1], 
                 yd[1]]

          dpts = [pya.DPoint(xtu[i], ytd[i]) for i in range(len(xtu))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element)
        
          # Adding the fishbone
          if (busfb):
            xstd = [r + w + cg +ii*w +(w - w_fb)/2,
                    r + w + cg +ii*w +(w - w_fb)/2 + w_fb,
                    r + w + cg +ii*w +(w - w_fb)/2 + w_fb,
                    r + w + cg +ii*w +(w - w_fb)/2]

            ystd = [(yu[3] - taperL),
                    (yu[3] - taperL),
                    (yd[1] + taperL),
                    (yd[1] + taperL)]

            dpts = [pya.DPoint(xstd[i], ystd[i]) for i in range(len(xstd))]
            dpolygon = DPolygon(dpts)
            element2 = Polygon.from_dpoly(dpolygon*(1.0/dbu))
            shapes(LayerSiN).insert(element2)  
          
        # Adding the top standard waveguide
        xTu = [r + w + cg,
               r + w + cg + w,
               r + w + cg + w/2 + wport/2,
               r + w + cg + w/2 - wport/2]
        
        yTu = [yu[3], 
               yu[3], 
               yu[3] + busL, 
               yu[3] + busL]
        
        dpts = [pya.DPoint(xTu[i], yTu[i]) for i in range(len(xTu))]
        dpolygon = DPolygon(dpts)
        element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
        shapes(LayerSiN).insert(element) 

        # Adding the bottom standard waveguide
        yTd = [yd[1], 
               yd[1],
               yd[1] - busL, 
               yd[1] - busL]
                
        dpts = [pya.DPoint(xTu[i], yTd[i]) for i in range(len(xTu))]
        dpolygon = DPolygon(dpts)
        element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
        shapes(LayerSiN).insert(element) 
        

        # Storing temp wg width, bus length, and gap because they are modified in the DEV BOX
        # These are used if a drop waveguide is used
        w_temp = w
        bus_length_temp = bus_length

        # Create the pins on the waveguides, as short paths:        
        w = to_itype(self.w, dbu)
        bus_length = to_itype(bus_length/2,dbu)

        # Pin 1
        t = pya.DTrans(pya.Trans.R0, (xTu[-1] + wport/2)/dbu, yTu[-1]/dbu)
        pin = pya.Path([pya.DPoint(0, -pin_length/2), pya.DPoint(0, pin_length/2)], wport/dbu) #500 is width of std WG
        pin_t = pin.transformed(t)
        shapes(LayerPinRecN).insert(pin_t)
        text = pya.Text ("opt1", t)
        shape = shapes(LayerPinRecN).insert(text)
        shape.text_size = 0.4/dbu

        # Pin 2
        t = pya.DTrans(Trans.R180, (xTu[-1] + wport/2)/dbu, yTd[-1]/dbu)
        pin = Path([Point(0, -pin_length/2), Point(0, pin_length/2)], wport/dbu) #500 is width of std WG
        pin_t = pin.transformed(t)
        shapes(LayerPinRecN).insert(pin_t)
        text = Text ("opt2", t)
        shape = shapes(LayerPinRecN).insert(text)
        shape.text_size = 0.4/dbu


        #####################################
        ############# Bus Wg 2 #############
        ###################################
        if (num_busses > 1):
          
          # Reinitializing the values that were modified in the DEV-BOX
          w = w_temp
          bus_length = bus_length_temp
          
          s1 = p*ff2 #silicon
          s2 = p - s1 #gap

          r = self.r # resetting r
          const = math.floor(2*pi*r/(s1 + s2))

          #if doesn't divide evenly, replace r with best possible r
          if ((2*pi*r)%(s1 + s2) != 0):
              r = const*(s1 + s2)/(2*pi)
          
          #calulate ideal length of bus
          bus_length = busL
                      
          for ii in range(1):
            
            # the middle SWG
            xo = [-(r + w + cg + ii*w),
                  -(r + w + cg + w + ii*w),
                  -(r + w + cg + w + ii*w),
                  -(r + w + cg + ii*w)]

            yo = [0, 0, s1, s1]
            
            # Checking for bus symmetry 
            bus_axis = self.calculate_centroid_bus(yo)
            diff_axis = bus_axis - ring_axis_left
    
            # SWG is above the bus, shift the bus upward
            if (diff_axis < -0.0001):
              while (diff_axis < -0.0001):
                yo = [yo[0] + 0.0001, yo[1] + 0.0001, yo[2] + 0.0001, yo[3] + 0.0001]
                bus_axis = self.calculate_centroid_bus(yo)
                diff_axis = bus_axis - ring_axis_left

            # SWG is below the bus, shift the bus down
            elif (diff_axis > 0.0001 ):
              while (diff_axis > 0.0001):
                yo = [yo[0] - 0.0001, yo[1] - 0.0001, yo[2] - 0.0001, yo[3] - 0.0001]
                bus_axis = self.calculate_centroid_bus(yo)
                diff_axis = bus_axis - ring_axis_left
            
            dpts = [pya.DPoint(xo[i], yo[i]) for i in range(len(xo))]
            dpolygon = DPolygon(dpts)
            element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
            shapes(LayerSiN).insert(element)

            n = int(math.ceil((constant))) # SWG Gratings (before the taper) above and below the central grating (minus one)  
            for i in range(n):
              yu = [yo[j] + i*p for j in range(len(yo))] # n-1 SWG's above the middle SWG
              yd = [yo[j] - i*p for j in range(len(yo))] # n-1 SWG below the middle SWG
                
              dpts = [pya.DPoint(xo[i], yu[i]) for i in range(len(xo))]
              dpolygon = DPolygon(dpts)
              element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
              shapes(LayerSiN).insert(element)
              dpts = [pya.DPoint(xo[i], yd[i]) for i in range(len(xo))]
              dpolygon = DPolygon(dpts)
              element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
              shapes(LayerSiN).insert(element) 
            
            # draw the tapers from waveguide to SWG
            xtu = [-((r + w + cg + ii*w) + (w - w_fb)/2),
                   -((r + w + cg + ii*w) + (w - w_fb)/2 + w_fb),
                   -((r + w + cg + ii*w) + w),
                   -(r + w + cg + ii*w)]
            
            ytu = [yu[3] - taperL, 
                   yu[3] - taperL, 
                   yu[3], 
                   yu[3]]

            dpts =[pya.DPoint(xtu[i], ytu[i]) for i in range(len(xtu))]
            dpolygon = DPolygon(dpts)
            element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
            shapes(LayerSiN).insert(element)
            
            ytd = [yd[1] + taperL, yd[1] + taperL, yd[1], yd[1]]
            dpts =[pya.DPoint(xtu[i], ytd[i]) for i in range(len(xtu))]
            dpolygon = DPolygon(dpts)
            element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
            shapes(LayerSiN).insert(element)

            # Add the fishbone 
            if (busfb):
              xstd = [-((r + w + cg + ii*w) + (w - w_fb)/2),
                      -((r + w + cg + ii*w) + (w - w_fb)/2 + w_fb),
                      -((r + w + cg + ii*w) + (w - w_fb)/2 + w_fb),
                      -((r + w + cg + ii*w) + (w - w_fb)/2)]
              
              ystd = [yu[3] - taperL, 
                      yu[3] - taperL, 
                      yd[1] + taperL, 
                      yd[1] + taperL]

              dpts=[pya.DPoint(xstd[i], ystd[i]) for i in range(len(xstd))]
              dpolygon = DPolygon(dpts)
              element2 = Polygon.from_dpoly(dpolygon*(1.0/dbu))
              shapes(LayerSiN).insert(element2)  
            
          # taper connections from multi-tapers to std WG
          xTu = [-(r + w + cg), 
                -(r + w + cg + w),
                -(r + w + cg + w/2 + wport/2), 
                -(r + w + cg + w/2 - wport/2)]
          
          yTu = [yu[3], 
                 yu[3], 
                 yu[3] + busL, 
                 yu[3] + busL]

          dpts = [pya.DPoint(xTu[i], yTu[i]) for i in range(len(xTu))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element) 

          # Adding the bottom standard waveguide
          yTd = [yd[1], 
                yd[1],
                yd[1] - busL, 
                yd[1] - busL]
          
          dpts = [pya.DPoint(xTu[i], yTd[i]) for i in range(len(xTu))]
          dpolygon = DPolygon(dpts)
          element = Polygon.from_dpoly(dpolygon*(1.0/dbu))
          shapes(LayerSiN).insert(element) 
          
          # Create the pins on the waveguides, as short paths:
          w = to_itype(self.w,dbu)
          bus_length = to_itype(bus_length/2,dbu)

          # Pin 3
          t = pya.DTrans(pya.Trans.R0, (xTu[-1] - wport/2)/dbu, yTu[-1]/dbu)
          pin = pya.Path([pya.DPoint(0, -pin_length/2), pya.DPoint(0, pin_length/2)], wport/dbu)
          pin_t = pin.transformed(t)
          shapes(LayerPinRecN).insert(pin_t)
          text = pya.Text ("opt3", t)
          shape = shapes(LayerPinRecN).insert(text)
          shape.text_size = 0.4/dbu

          # Pin 4
          t = pya.DTrans(Trans.R180, (xTu[-1] - wport/2)/dbu, yTd[-1]/dbu)
          pin = Path([Point(0, -pin_length/2), Point(0, pin_length/2)], wport/dbu)
          pin_t = pin.transformed(t)
          shapes(LayerPinRecN).insert(pin_t)
          text = Text ("opt4", t)
          shape = shapes(LayerPinRecN).insert(text)
          shape.text_size = 0.4/dbu

      # DEV BOX
      # Encapsulate the pcell within a box for error checking
      w = self.w

      if (num_busses != 0):
        dev = pya.DBox(-(r + w + cg + w), 
                        yTd[-1], 
                        r + w + cg + w,
                        yTu[-1])
      else:
        dev = pya.DBox(-(r + w), 
                       r + w, 
                       r + w,
                       -(r + w))
                  
      shapes(LayerDevRecN).insert(dev)