# coding=utf-8

import platform
if platform.system() == 'Windows':
    import PyV8
else:
    from pyv8 import PyV8

ctxt = PyV8.JSContext()
ctxt.enter()


def get_userresponse(distance, challenge):
    # print distance, challenge
    # print type(distance), type(challenge)
    challenge = challenge.encode('ascii')
    func = ctxt.eval("""
    (function(){
            function f(a,b) {
            for (var c = b.slice(32), d = [], e = 0; e < c.length; e++) {
                var f = c.charCodeAt(e);
                d[e] = f > 57 ? f - 87 : f - 48
            }
            c = 36 * d[0] + d[1];
            var g = Math.round(a) + c;
            b = b.slice(0, 32);
            var h, i = [[], [], [], [], []], j = {}, k = 0;
            e = 0;
            for (var l = b.length; e < l; e++)
                h = b.charAt(e), j[h] || (j[h] = 1, i[k].push(h), k++, k = 5 == k ? 0 : k);
            for (var m, n = g, o = 4, p = "", q = [1, 2, 5, 10, 50]; n > 0;)
                n - q[o] >= 0 ? (m = parseInt(Math.random() * i[o].length, 10), p += i[o][m], n -= q[o]) : (i.splice(o, 1), q.splice(o, 1), o -= 1);
            return p
        };
        return f(%d, '%s');
        })
    """ % (distance, challenge))
    res = func()
    # print 'res', res
    return res


# print get_userresponse(162 , '92e953613c6129087c7d9370cd0a402d')


def get_a(trail_arr):

    func = ctxt.eval(
        '''
        (function(){

            var a = function(a, b) {
                Q.p("arr", [a], b)
            }, b = function(a, b) {
                Q.f("arr", b).push(a)
            }, c = function(a) {
                for (var b, c, d, e = [], f = 0, g = [], h = 0, i = a.length - 1; h < i; h++)
                    b = Math.round(a[h + 1][0] - a[h][0]), c = Math.round(a[h + 1][1] - a[h][1]), d = Math.round(a[h + 1][2] - a[h][2]), g.push([b, c, d]), 0 == b && 0 == c && 0 == d || (0 == b && 0 == c ? f += d : (e.push([b, c, d + f]), f = 0));
                return 0 !== f && e.push([b, c, f]), e
            }, d = function(a) {
                var b = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr", c = b.length, d = "", e = Math.abs(a), f = parseInt(e / c);
                f >= c && (f = c - 1), f && (d = b.charAt(f)), e%=c;
                var g = "";
                return a < 0 && (g += "!"), d && (g += "$"), g + d + b.charAt(e)
            }, e = function(a) {
                for (var b = [[1, 0], [2, 0], [1, - 1], [1, 1], [0, 1], [0, - 1], [3, 0], [2, - 1], [2, 1]], c = "stuvwxyz~", d = 0, e = b.length; d < e; d++)
                    if (a[0] == b[d][0] && a[1] == b[d][1])
                        return c[d];
                return 0
            }, f = function(a) {
                for (var b, f = c(a), g = [], h = [], i = [], j = 0, k = f.length; j < k; j++)
                    b = e(f[j]), b ? h.push(b) : (g.push(d(f[j][0])), h.push(d(f[j][1]))), i.push(d(f[j][2]));
                return g.join("") + "!!" + h.join("") + "!!" + i.join("")
            };
        return f('''+str(trail_arr)+''')
        })
        '''
    )
    return func()


def get_validate_offline(challenge):
    func = ctxt.eval(r'''
    (function(){
    var getX = function(a) {
        if (5 == a.length) {
            var b = 200,
            c = parseInt(a, 16) || 0,
            d = c % b;
            return d < 40 && (d = 40),
            d
        }
    };

    var md5 = function(a) {
        function b(a, b) {
            return a << b | a >>> 32 - b
        }
        function c(a, b) {
            var c, d, e, f, g;
            return e = 2147483648 & a,
            f = 2147483648 & b,
            c = 1073741824 & a,
            d = 1073741824 & b,
            g = (1073741823 & a) + (1073741823 & b),
            c & d ? 2147483648 ^ g ^ e ^ f: c | d ? 1073741824 & g ? 3221225472 ^ g ^ e ^ f: 1073741824 ^ g ^ e ^ f: g ^ e ^ f
        }
        function d(a, b, c) {
            return a & b | ~a & c
        }
        function e(a, b, c) {
            return a & c | b & ~c
        }
        function f(a, b, c) {
            return a ^ b ^ c
        }
        function g(a, b, c) {
            return b ^ (a | ~c)
        }
        function h(a, e, f, g, h, i, j) {
            return a = c(a, c(c(d(e, f, g), h), j)),
            c(b(a, i), e)
        }
        function i(a, d, f, g, h, i, j) {
            return a = c(a, c(c(e(d, f, g), h), j)),
            c(b(a, i), d)
        }
        function j(a, d, e, g, h, i, j) {
            return a = c(a, c(c(f(d, e, g), h), j)),
            c(b(a, i), d)
        }
        function k(a, d, e, f, h, i, j) {
            return a = c(a, c(c(g(d, e, f), h), j)),
            c(b(a, i), d)
        }
        function l(a) {
            for (var b, c = a.length,
            d = c + 8,
            e = (d - d % 64) / 64, f = 16 * (e + 1), g = Array(f - 1), h = 0, i = 0; i < c;) b = (i - i % 4) / 4,
            h = i % 4 * 8,
            g[b] = g[b] | a.charCodeAt(i) << h,
            i++;
            return b = (i - i % 4) / 4,
            h = i % 4 * 8,
            g[b] = g[b] | 128 << h,
            g[f - 2] = c << 3,
            g[f - 1] = c >>> 29,
            g
        }
        function m(a) {
            var b, c, d = "",
            e = "";
            for (c = 0; c <= 3; c++) b = a >>> 8 * c & 255,
            e = "0" + b.toString(16),
            d += e.substr(e.length - 2, 2);
            return d
        }
        function n(a) {
            a = a.replace(/\r\n/g, "\n");
            for (var b = "",
            c = 0; c < a.length; c++) {
                var d = a.charCodeAt(c);
                d < 128 ? b += String.fromCharCode(d) : d > 127 && d < 2048 ? (b += String.fromCharCode(d >> 6 | 192), b += String.fromCharCode(63 & d | 128)) : (b += String.fromCharCode(d >> 12 | 224), b += String.fromCharCode(d >> 6 & 63 | 128), b += String.fromCharCode(63 & d | 128))
            }
            return b
        }
        var o, p, q, r, s, t, u, v, w, x = [],
        y = 7,
        z = 12,
        A = 17,
        B = 22,
        C = 5,
        D = 9,
        E = 14,
        F = 20,
        G = 4,
        H = 11,
        I = 16,
        J = 23,
        K = 6,
        L = 10,
        M = 15,
        N = 21;
        for (a = n(a), x = l(a), t = 1732584193, u = 4023233417, v = 2562383102, w = 271733878, o = 0; o < x.length; o += 16) p = t,
        q = u,
        r = v,
        s = w,
        t = h(t, u, v, w, x[o + 0], y, 3614090360),
        w = h(w, t, u, v, x[o + 1], z, 3905402710),
        v = h(v, w, t, u, x[o + 2], A, 606105819),
        u = h(u, v, w, t, x[o + 3], B, 3250441966),
        t = h(t, u, v, w, x[o + 4], y, 4118548399),
        w = h(w, t, u, v, x[o + 5], z, 1200080426),
        v = h(v, w, t, u, x[o + 6], A, 2821735955),
        u = h(u, v, w, t, x[o + 7], B, 4249261313),
        t = h(t, u, v, w, x[o + 8], y, 1770035416),
        w = h(w, t, u, v, x[o + 9], z, 2336552879),
        v = h(v, w, t, u, x[o + 10], A, 4294925233),
        u = h(u, v, w, t, x[o + 11], B, 2304563134),
        t = h(t, u, v, w, x[o + 12], y, 1804603682),
        w = h(w, t, u, v, x[o + 13], z, 4254626195),
        v = h(v, w, t, u, x[o + 14], A, 2792965006),
        u = h(u, v, w, t, x[o + 15], B, 1236535329),
        t = i(t, u, v, w, x[o + 1], C, 4129170786),
        w = i(w, t, u, v, x[o + 6], D, 3225465664),
        v = i(v, w, t, u, x[o + 11], E, 643717713),
        u = i(u, v, w, t, x[o + 0], F, 3921069994),
        t = i(t, u, v, w, x[o + 5], C, 3593408605),
        w = i(w, t, u, v, x[o + 10], D, 38016083),
        v = i(v, w, t, u, x[o + 15], E, 3634488961),
        u = i(u, v, w, t, x[o + 4], F, 3889429448),
        t = i(t, u, v, w, x[o + 9], C, 568446438),
        w = i(w, t, u, v, x[o + 14], D, 3275163606),
        v = i(v, w, t, u, x[o + 3], E, 4107603335),
        u = i(u, v, w, t, x[o + 8], F, 1163531501),
        t = i(t, u, v, w, x[o + 13], C, 2850285829),
        w = i(w, t, u, v, x[o + 2], D, 4243563512),
        v = i(v, w, t, u, x[o + 7], E, 1735328473),
        u = i(u, v, w, t, x[o + 12], F, 2368359562),
        t = j(t, u, v, w, x[o + 5], G, 4294588738),
        w = j(w, t, u, v, x[o + 8], H, 2272392833),
        v = j(v, w, t, u, x[o + 11], I, 1839030562),
        u = j(u, v, w, t, x[o + 14], J, 4259657740),
        t = j(t, u, v, w, x[o + 1], G, 2763975236),
        w = j(w, t, u, v, x[o + 4], H, 1272893353),
        v = j(v, w, t, u, x[o + 7], I, 4139469664),
        u = j(u, v, w, t, x[o + 10], J, 3200236656),
        t = j(t, u, v, w, x[o + 13], G, 681279174),
        w = j(w, t, u, v, x[o + 0], H, 3936430074),
        v = j(v, w, t, u, x[o + 3], I, 3572445317),
        u = j(u, v, w, t, x[o + 6], J, 76029189),
        t = j(t, u, v, w, x[o + 9], G, 3654602809),
        w = j(w, t, u, v, x[o + 12], H, 3873151461),
        v = j(v, w, t, u, x[o + 15], I, 530742520),
        u = j(u, v, w, t, x[o + 2], J, 3299628645),
        t = k(t, u, v, w, x[o + 0], K, 4096336452),
        w = k(w, t, u, v, x[o + 7], L, 1126891415),
        v = k(v, w, t, u, x[o + 14], M, 2878612391),
        u = k(u, v, w, t, x[o + 5], N, 4237533241),
        t = k(t, u, v, w, x[o + 12], K, 1700485571),
        w = k(w, t, u, v, x[o + 3], L, 2399980690),
        v = k(v, w, t, u, x[o + 10], M, 4293915773),
        u = k(u, v, w, t, x[o + 1], N, 2240044497),
        t = k(t, u, v, w, x[o + 8], K, 1873313359),
        w = k(w, t, u, v, x[o + 15], L, 4264355552),
        v = k(v, w, t, u, x[o + 6], M, 2734768916),
        u = k(u, v, w, t, x[o + 13], N, 1309151649),
        t = k(t, u, v, w, x[o + 4], K, 4149444226),
        w = k(w, t, u, v, x[o + 11], L, 3174756917),
        v = k(v, w, t, u, x[o + 2], M, 718787259),
        u = k(u, v, w, t, x[o + 9], N, 3951481745),
        t = c(t, p),
        u = c(u, q),
        v = c(v, r),
        w = c(w, s);
        var O = m(t) + m(u) + m(v) + m(w);
        return O.toLowerCase()
    };

    var t = function(a, b) {
        // alert(a);
        for (var c = b.slice(32), d = [], e = 0; e < c.length; e++) {
            var f = c.charCodeAt(e);
            d[e] = f > 57 ? f - 87 : f - 48
        }
        c = 36 * d[0] + d[1];
        var g = Math.round(a) + c;
        b = b.slice(0, 32);
        var h, i = [[], [], [], [], []],
        j = {},
        k = 0;
        e = 0;
        for (var l = b.length; e < l; e++) h = b.charAt(e),
        j[h] || (j[h] = 1, i[k].push(h), k++, k = 5 == k ? 0 : k);
        for (var m, n = g,
        o = 4,
        p = "",
        q = [1, 2, 5, 10, 50]; n > 0;) n - q[o] >= 0 ? (m = parseInt(Math.random() * i[o].length, 10), p += i[o][m], n -= q[o]) : (i.splice(o, 1), q.splice(o, 1), o -= 1);
        return p
    };
    var d = parseInt(6 * Math.random()), e = parseInt(300 * Math.random());

    for (var f = md5(d + "").slice(0, 9), g = md5(e + "").slice(10, 19), h = "", i = 0; i < 9; i++) h += i % 2 == 0 ? f.charAt(i) : g.charAt(i);
    var k = h.slice(4),l = getX(k);
    var challenge = '__challenge__';
    return t(l, challenge) + "_" + t(d, challenge) + "_" + t(e,challenge)
    })
    '''.replace('__challenge__', challenge)
    )
    return func()

# print get_validate_offline('86c178279885c542901f346eb9134a66')


def get_distance(f, g):
    func = ctxt.eval(r'''
    (function(){
    var getX = function(a) {
        if (5 == a.length) {
            var b = 200,
            c = parseInt(a, 16) || 0,
            d = c % b;
            return d < 40 && (d = 40),
            d
        }
    };
    var f='__f__', g='__g__';
    for (h = "",i = 0;i < 9; i++) h += i % 2 == 0 ? f.charAt(i) : g.charAt(i);
    var k = h.slice(4);
    var l = getX(k);
    return l;
    })
    '''.replace('__f__', f).replace('__g__', g)
    )
    return func()


# print get_distance('c4ca4238a', 'caa6e02c9')
# print get_a([[1,2,3],[4,5,6]])

# func = ctxt.eval("""
# (function(){
#         function f(a) {
#
#         return a[0];
#     };
#     return f([[1,2,3],[4,5,6]]);
#     })
# """)
# print func()
