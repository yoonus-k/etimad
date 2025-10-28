# Etimad API Configuration
# Set USE_API to True to fetch from Etimad API (requires authentication)
# Set to False to use local all_tenders.json file

USE_API = True  # Now using API with cookies

# Authentication cookies from browser (copied from your request - Updated 2025-10-09)
COOKIES = {
    'Dammam': '!HY6FieDuXLnBOClEIvbxjUiiGaNtJ4JcTknw9y4hXZ0mYMYjB4qOKI5SkjsTiGQkFdaZHfKBTGnJEt8=',
    'Identity.TwoFactorUserId': 'CfDJ8LVS1qLcD3FLuWdwu-VCPoGz5Fws5Kwud1Dh4Titq9jWzUMW1p03d5umQ5qXf-0kBDRuOUAuAO8yZ7w6hob6BIbEgJVusR3y-gnyiuCZLsWBgpRDggGrLpoztZqQR7kORShu4KaMOk38IJrG-Xy_X8ZHSxDk1bwxH2ONlKQqoYEMzrEgo3HPafIZG4XBPG4Xb4iIxrcOxgmLQ2Si0ap51ig6kd-s4cUyvXZ_zgamG1NonD39NWQMslWuiPiLXlzQZbjk4QA72wV--S8cLB_2Unpo0LDRfgBH6rhY0t2LkAxiDgux6YnBPqF1HyKl04b8UUIrNc_1Mrz519UAOsjHzz0',
    'MobileAuthCookie': 'CfDJ8LULV64BQyFKpogY7wWb0oqkoyD0R0tZUGxFYMvL6g7XXotAz2iHY6lo-pTtmbVRtgUZJOmZmAk4TD8is-SAQ22hcNYb_QCwRg3bCtnGD7rPOJkms8JnuuO-vs5o3ypU5_HLxZVzmoaUH2Bh651cBVFRzNyBJeolgtWWFGgX9o5N1LS8yedEJp7KaHmg3h3zawdUuzyx-zqoDQB9n516X31V0qwJ8kSxynmppc4gYdCm2ja8KnRSX_16mVv095pjGg',
    'idsrv.session': '960C8B77262A8B8CD3E37066D5470974',
    'login.etimad.ssk4': 'CfDJ8LVS1qLcD3FLuWdwu-VCPoGCiu-PfBxLJV2LRRWwif9kmFpjgMdoSvMZPqn4EBXGEfVRQfoTZ2G6YyCjXZd3t3lGNC0KrsVLK_OK_3qa4qOFVWoQ3vmoiYx5Vk-jhCPgQgHeD-kBdLRY4AIkuE8p8oGDVZMpvxj_UYcQc-DH_edewf0Af-moZUypv4DsqVmlPGDhg-jxXObyM20hNyIjBotcRqV6efrw1EwASDb_THZxbbjkyiEBKR05N87np0AhJ1OfZatv7LmQTqRiQbvMYHta44DcJxJJJUnWfneh3dMR3En8UlkKsSSW2P1ssAo0Cia4Lhz2k2QBCwOphKQb8qVt5PSwuK5X1wZsBkL3rLWE',
}

# Maximum number of pages to fetch (each page has ~24 tenders)
MAX_PAGES = 100
