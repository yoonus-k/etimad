# Etimad API Configuration
# Set USE_API to True to fetch from Etimad API (requires authentication)
# Set to False to use local all_tenders.json file

USE_API = True  # Now using API with cookies

# Authentication cookies from browser (copied from your request - Updated 2025-10-09)
COOKIES = {
    'Dammam': '!UzakcSdzf0V8VwFEIvbxjUiiGaNtJyi1/GgGmKRrLBeCqrw6YXJInX+QboTWhqqKBelxBJgdlLkhf0E=',
    'Identity.TwoFactorUserId': 'CfDJ8IlMR2xrC51DkaOqgoGVnpdgY-X0TNlHxhOUlzLfsnuk1ETlf4B2kt8YgC-nV1u4H8HzraNL9Yy15FRVxQ0GrtR8ffOujhc0jBQ8wMJ4purL3n_MPQlv7yVGtE6-MuPR5pkxHMLwxGyNhc4NJYN4RkLE3FHRWB5QFfhA5buP5DvcZxM1-5Fyn2Ni6MIaM4QY6jeyoV7cjM2LP2pE73xGe_l4ai9e-TGykmyQ78jZ3rZmyAcKuV9Yg4S12RgkkHcppY4IVrQCSpx1R7Q3XjX1qo3toyy_Wq_4XXirSb4o32cKQs-w5WZ8lU9Nffnzhc5QTzZobd_sCG-KwWrUPV1xagE',
    'MobileAuthCookie': 'CfDJ8Nu6sOM3fcNEnk4Io4l_h_tJSMDMbdN-j1VA2yePBCYeAvud3I4Ub8LOFtcquYQfZP9g2a_zbrpRSiyzYYhZzosUdxrV5ihk5nlCzsCw0UdKGZx-Rr0n2qaHjRZUbl8nQtPTmQ_YI-tcg28q-de2RXjcUFpXHhvO2p7zjmjNtWumievlWH81K9i0_Ihe2dqg0LVzGJzWM19TraYxn2f87OaTQYp6TOQex91Z0bzo7zjWWWVjPIIQv-55RTPe6Y0jDw',
    'SameSite': 'None',
    'idsrv.session': '08C24204A949F2CABBAA761C333CBB9F',
    'login.etimad.ssk4': 'CfDJ8IlMR2xrC51DkaOqgoGVnpfg3EMx9Gceo6Nx9fi5lIfh_sVDZRnCSme9tqiEs_1oChvAocbB-HNZSgRp4ruLB8YyeZdmH4mQt66njkow9Uc9HPdGkRavlzByIj4eCUYQlI4q4R12KAl_1KDjfWxzKzgOSAsZ9D_XyVwBG8z6kU4GyiNiz4dtYM4sD67FWU4aMgeerJF2bAQ25ZS39d6_bqhj94o2BNhovIkjOB8vV8BJJJThIYm9dx4U69R0ux-zUlakxFEkeFgfyNz4uIeFzRmnzebLJdV3RH7fj89R2d3LG2JXytm8H4jq3-9damQFv5NDXyyoz9d2OjozxAT5EaM',
}

# Maximum number of pages to fetch (each page has ~24 tenders)
MAX_PAGES = 100
