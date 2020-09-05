def ds(h):
    """ The formula used by VVVVID to get real url from embed_code codes """

    g = "MNOPIJKL89+/4567UVWXQRSTEFGHABCDcdefYZabstuvopqr0123wxyzklmnghij"

    def f(m):
        l = []
        o = 0
        b = False
        m_len = len(m)

        while ((not b) and o < m_len):
            n = m[o] << 2
            o += 1
            k = -1
            j = -1

            if o < m_len:
                n += m[o] >> 4
                o += 1

                if o < m_len:
                    k = (m[o - 1] << 4) & 255
                    k += m[o] >> 2
                    o += 1

                    if o < m_len:
                        j = (m[o - 1] << 6) & 255
                        j += m[o]
                        o += 1
                    else:
                        b = True

                else:
                    b = True

            else:
                b = True

            l.append(n)

            if k != -1:
                l.append(k)

            if j != -1:
                l.append(j)

        return l

    c = []
    for e in h:
        c.append(g.index(e))

    c_len = len(c)
    for e in range(c_len * 2 - 1, -1, -1):
        a = c[e % c_len] ^ c[(e + 1) % c_len]
        c[e % c_len] = a

    c = f(c)
    d = ''
    for e in c:
        d += chr(e)

    return d


