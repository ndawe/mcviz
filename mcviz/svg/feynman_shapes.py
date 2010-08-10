from __future__ import division

from spline import Spline

default_amp = 8

def set_width(width):
    global max_amp
    max_amp = width

# Functions to get photon splines

def get_photon_splines(length, amplitude, n_waves, power, amp):
    N = n_waves * 2
    wavelength = length / N
    cntrl_strength = wavelength / 2
    
    # scaling envelope 
    if power:
        envelope = [1 - abs(2*i/(N-1) - 1)**power for i in range(N)]
    else:
        envelope = [1 for i in range(N)]

    # x offsets of points:
    px = [0.0] + [wavelength * (0.5 + i) for i in range(N)]
    px.append(px[-1] + wavelength / 2)

    # y offsets of points:
    py = [0.0] + [amplitude * envelope[i] for i in range(N)] + [0.0]
    
    splines = []
    sgn = 1
    for i in range(1, N+2):
        op  = px[i-1], -sgn * px[i-1]
        cp1 = px[i-1] + cntrl_strength, -sgn * py[i-1]
        cp2 = px[i] - cntrl_strength, sgn * py[i]
        dp  = px[i], sgn * py[i]
        if i == 1:
            cp1 = op
        elif i == N+1:
            cp2 = dp
        splines.append(Spline(op, cp1, cp2, dp))
        sgn = -sgn
    return splines

def get_gluon_splines(length, amplitude, n_waves, amp): 
    loopyness = 0.7
    init_length = 2

    N = n_waves * 2 + 1
    wavelength = length / (N - 1 + 2*init_length)
    cntrl_strength = wavelength * loopyness
    
    # x offsets of points:
    px = [0.0] + [wavelength * (init_length + i) for i in range(N)]
    px.append(px[-1] + init_length * wavelength)

    # y offsets of points:
    py = [0.0] + [amplitude for i in range(N)] + [0.0]
    
    splines = []
    sgn = 1
    for i in range(1, N+2):
        op  = px[i-1], -sgn * px[i-1]
        cp1 = px[i-1] - sgn * (2 - sgn) * cntrl_strength, -sgn * py[i-1]
        cp2 = px[i] - sgn * (2 + sgn) * cntrl_strength, sgn * py[i]
        dp  = px[i], sgn * py[i]
        if i == 1:
            cp1 = op
        elif i == N+1:
            cp2 = dp
        splines.append(Spline(op, cp1, cp2, dp))
        sgn = -sgn
    return splines
    
def pathdata_from_splines(splines, trafo_spline = None):
    if trafo_spline:
        splines = [trafo_spline.transform_spline(s) for s in splines]
    data = ["M %.5f %.5f\n" % splines[0].points[0]]
    for s in splines:
        data.append('C %.5f %.5f %.5f %.5f %.5f %.5f\n' % (s.points[1] + s.points[2] + s.points[3]))
    return "".join(data)


# Functions to get SVN path data for objects
# contain some policy

def photon_data(energy, length = None, spline = None, n_max = 10, n_min = 3,
                power = 10, amp = default_amp):
    """Get the SVG path data for a photon. 
    energy must be between 0 and 1
    either length or spline must be given."""
    assert length or spline and not (length and spline)
    if spline:
        length = spline.length
    # Here are parametrizations:
    energy = min(1, max(0,energy))
    amplitude = (0.5 + 0.5*energy) * amp
    n_per_50 = n_min + energy * (n_max - n_min)
    n = max(2, int(n_per_50 * length / 50))
    splines = get_photon_splines(length, amplitude, n, power, amp)
    return pathdata_from_splines(splines, trafo_spline = spline)

def gluon_data(energy, length = None, spline = None, n_max = 11, n_min = 1, 
               amp = default_amp):
    """Get the SVG path data for a gluon.
    energy must be between 0 and 1
    either length or spline must be given."""
    assert length or spline and not (length and spline)
    if spline:
        length = spline.length
    # Here are parametrizations:
    energy = min(1, max(0,energy))
    amplitude = (1 - 0.3*energy) * amp
    n_per_50 = n_min + energy * (n_max - n_min)
    n = max(1, int(n_per_50 * length / 50))
    splines = get_gluon_splines(length, amplitude, n, amp)
    return pathdata_from_splines(splines, trafo_spline = spline)

def boson_data(energy, length = None, spline = None, n_max = 2, n_min = 2):
    """Get the SVG path data for a boson.
    energy must be between 0 and 1
    either length or spline must be given."""
    a = default_amp / 3
    return photon_data(energy, length, spline, n_max, n_min, power = None, amp = a)

if __name__=="__main__":
    from spline import Spline, SplineLine
    
    spline1 = Spline((5.0, -10), (20.000, -10), (15.0, 30.000), (40.0, 10.000))
    spline2 = Spline((40, 10), (65, -10), (60, 30), (80, 20))
    spline = SplineLine((spline1, spline2))
    print spline.length


    s = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1000 1000">\n']

    s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (10, 10, spline.svg_path_data))
    #s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (10, 10, dat2))


    n = 10
    for i in range(n+1):
        x = 10
        y = 40 + i*25
        e = i/n
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (x, y, photon_data(e, spline.length)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (100+x, y, photon_data(e, spline = spline)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (200+x, y, gluon_data(e, spline.length)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (300+x, y, gluon_data(e, spline = spline)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (400+x, y, boson_data(e, spline.length)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (500+x, y, boson_data(e, spline = spline)))

    for i in range(n+1):
        x = 10
        y = 400 + i*25
        e = 0.6
        l = (i + 0.5) / n * 180
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (x, y, photon_data(e, l)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (250+x, y, gluon_data(e, l)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (500+x, y, boson_data(e, l)))

    #s.append('<path transform="translate(10,10)" fill="none" stroke="red" id="u" d="%s" />\n' % (gluon(0.5, 200)))

    s.append('" />\n')
    s.append('</svg>\n')

    f = file("photon.svg","w")
    f.write("".join(s))
    f.close()

    print "Written photon.svg."