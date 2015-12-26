import factory

from django.utils import timezone

from ...models import BaseTransaction


class BaseTransactionFactory(factory.DjangoModelFactory):
    class Meta:
        model = BaseTransaction

    tx = ('enc1:::d9fbf0312906ffcc085145bd0f4f1df7de0cd43dc037cfffe4243c03fd'
          '5b5486enc2:::GJirsgc6CyK66MQWLMBQPLzYoGUOxWSXE8MhPgvIqP0bRmAWXaI2D'
          'smF7Dj5pqavIQ/lnGpUFz/F4DTlSOIg+8FbtUuiu2E9PoKfkj7i0AAPUl2OVl1TKUM'
          'QRHBVkUDgd6M9zePh/a4tE9dyw1FBVSIdYZnCXb9jsZ0+3YksTCwxOO3V6qkLhQnr5'
          'S/Ptooka3yvpFhSUOhMszDGUQzYfExlYFIXkmKHgL9WWAZa5PiCi/HgVdNOHkm6BNJ'
          'KbmZxgfno39v69+8JoNdmp4uns2BiBmDEkJ8vSxDufmfUO3Zt3u+vxNYPDVlIkmzfvK'
          'dV2nnn/707Wp65w3LyMyWxc9TX45RFQJkkAIxCtgzZ6loJjBdbSKA0feJOI7YNeQD0w'
          'E6kY2/7BwNySUn3YsE3U9aMHAzoMXY8jxjXSNBAqJuASqux3uliwQWSoMZD6MlIg5TY'
          'sH4bSBNu5n3VN7IJoDyZULEP1neU3Wc5iOwvMx5wegDI6iGfteIS5RKz/r+H6mMHLEl'
          'ZDssqwgaCaA/oTFoxn90IyvH6Zdub0WsAM3VqMmfKmlSqFOB7Xf5Jw/RlqDHUwZ49JG'
          'ciEBUKYe8Ojmoj4uNYyXJgvouu6eyXg5SQfdswDG4tNZcbcSRwRtvkPHBW7KnvDnc32'
          '1fQkb0z7TOhmUsXuwFyyt5bbYHeK/CsYTwkE079HFFwthqHE3CTOFVXv4IHKYYLj8Bi'
          'JSG0R/j6ciySozBzosWV7uNzeKiOZoy8uoh6pBBIrpUbz2+6b/id6nkyRHzATxS8RuZ'
          '0COwzemgZc9Y/6QCyIw/w5JlcWY1zLMEioGzLPRmfKvbr0Rk1/jabH3drDIsXvVrlCW'
          'OX5XGvbJhy7+r+Pq2bdfjM6Izrb92B2M5ktgGtli8TnCb6n7U97aqVzcxmlLjaGR/Z9K'
          'YDtBWHAy4P4KoLDW0X0aSZ9tsBxwGcvzCKBTvCNZZvk6dETaIBHk3BHUDBZXlbbFld6K'
          'IWJYoPe6+wyV3Y24/JFJJo2H7DfEnKsWQ0SwCdYIaFpII4cm2sqQBh2l2Rm9UR3GnW7q'
          'So0yCGc+zDDqWc76Bzlb2VHMsfv2PYKgyWPM7f1cJSVPFplfUSddFcyWG7849QZnypMJ'
          'rIRnKDVCcXcpavR1WRFnZ6xOBGL7TTTmpuTpdZ9W4pL1trGKyQzdRHLsnpTZ2oqBCQ4j'
          'biQqWINn4aE1dpY1FbWlgp11IXYMIMhxqCs/r9mwj+e4s18fra/bel4U40vISNOZuy5g'
          'J5ylqcB/nd/U/54wEP+RGi/vO3cB7pOBgIAGdFaroyY5C6t0TbhmM36/8YPsyNqvsRmM'
          '3OskdAo0JB/271lcD60PPy1UTj7kD1biYdAEzxiil7QwwnjJ/YXw5s0xJt6CnRNZvI4h'
          'QDqIrxjdsc9ZLOjVaZSCShuf220IeDa7qIpQCJR6kNGoPJTzU5RrRh90VQ9T+GNXtoPYD'
          'i/BZ0FDaW/jfiBWXaex7dyVW6r3EPn7xoCb80drh4M2tZhmX6Gh9mVlOELNgtHj3dGxPk'
          'xJj9OuA0iKjUpqcG8kIsq/tkgykhLoyR3w3j2qNlCWnxn5rOEk/LGaLPpQyk2KZGp3qcx'
          'X4Emdv4i29mxIqhPmKNJk2djE9m+f/QldGnpcNfXF71ucdcG0R3QRl2/kMAXNEneDJxm/+'
          'IO/czgteqST36nJrCR/rEHqLgOM2tCFbjTEOH3jr3cOWrp8mQfYwRRESZCtW4dBJzjf2yL'
          'iksn3NkXVyBaRYOXOjmjwt2ewkAKYVEsFXftECfi+5GpWQ7nsi777Bjv5aZvr5S7oO+3wp'
          'ZZv7O+32J8WlieRUKpQGCmgsfgM5FYAZiiWMWLeoa2volY2gEXNc0jm0/s+fZkEUGcn3iR'
          'UdHg6Bf9CsdPlfTyuOAElJe70/1gxLMJdtYCWlYfUId56iEBBl+Of/V5yBf/yFCgI24R92'
          'CZjCxuyK+ITloOPRChjUf3Lorex980s55uVRU3PFUenRsWo7/xo0la/+09r6Wdsfh/HxMfq'
          'anM6B4X3+ptmTCvaKB2ZVRAeS7j3/05xfH87ozF6tuwpNiE+sTHdahH5l3nZYuLc/iWJYOZ'
          'MxCn8Sxy+QoKpzDFvhnI5kD+E2GrAKQxOoyela71/hh1bCMKGkJzCybKgM9vojov6O9fYZm4'
          '7pLoeT0qxa/Z+y3QEnTRlVat7HYCY4/qs0IUGK7kW/hXCsIvSZwk/nAeuha6Y3EX1uDgVZno'
          'BuTATj+VXnb6aNO6o+73BhlIK9kXenH+T16QACepRx3S7qqJG032EqKL+4CnnQ8MuYfZ0'
          '++ID8EFLUfYBuxtQXlvuDjPIjEyOdf2PlOV4LmhTLU6vGZKXIk5NnvEiGcshx4wYKjbH5H'
          'Jfhlo5PEsSCO+RBjYL6yxkpNy/hWMlq8XKbXx2C15ChHOeVEi6jW/KqkM5juvpdlGs37of'
          'Aw2f/1apeShVx+UrCDlLODAWKG9NQatiBEJsOYmTs69u/JOshsZpnQ801Ywo4B61N+Uees'
          'iKla1C8YPHHMkNplVhpq4u7s7+7/Ml8tYBY/3yjhuKCHyVGmE3xPDgO3eTOBeMyJR08fbUeL'
          'sJPlYNfJURmVS64nItzoKsjoOwz+B7u0hrLBmgNK9mrlFR7QRlXc5d1k9JNBq7hRWybaJCi'
          'LhsDoRaWVThCzTOuT0Lq912dBzt7Rxaxl5aTKLlCZyIzAoVhy5Q1eX5n23qE6JJpBau25Rm'
          'K+Es+YGcGlb9zopTlCiv:::RE2ZyTuikFIDmHUey0RRog==')
    tx_name = 'SubjectRequisition'
    tx_pk = '5dac69c2-57a6-4da8-923a-91d3186d021c'
    producer = 'mpp54-bhp066_survey'
    action = 'I'
    timestamp = '20130809170439931625'
    consumed_datetime = timezone.now()
    is_ignored = False
    is_error = False
