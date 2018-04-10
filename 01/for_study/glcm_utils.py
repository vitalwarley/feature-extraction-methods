#!/usr/bin/env python

# Código feito por latived, baseado no tutorial "Measuring Texture and Color"
# Replicação do artigo: Texture-based polyp detection in colonoscopy

# Funções:
#   calc_glcm(patch, disp)  -> retorna glcm para o patch usando um displacement
#   calc_attrs(glcm)        -> retorn atributos extraídos da glcm 

import numpy as np

def calc_glcm(patch=None, disp=[0,1]):
    #       recebe patch
    #       retorna glcm

    displacement = disp # padrão usado
    
    # Image para ndarray
    PATCH_SIZE = len(patch)

    # ROWMAX e COLMAX são as bordas utilizadas para o cálculo da matriz GLCM
    rowmax  =   PATCH_SIZE - displacement[0] if displacement[0] else PATCH_SIZE - 1
    colmax  =   PATCH_SIZE - displacement[1] if displacement[1] else PATCH_SIZE - 1

    GRAY_LEVELS = 256 # total de níveis vai ser tam da GLCM

    # inicializa matriz GLCM
    shape = (GRAY_LEVELS, GRAY_LEVELS)
    glcm = np.zeros(shape=shape, dtype=np.int8)
    
    # Calculando GLCM para patch
    # TODO: verificar se há como melhorar 
    for i in range(rowmax):
        for j in range(colmax):
            # pega valores (m,n) no padrão setado e incrementa glcm[m][n] e glcm[n][m]
            m, n = patch[i][j], patch[i + displacement[0]][j + displacement[1]]
            # simétrica
            glcm[m][n] += 1
            glcm[n][m] += 1
    return glcm

def calc_attrs(glcm = None):
    #       recebe glcm
    #       retorna lista de atributos

    # TODO: inserir novos atributos de acordo com artigo original (ver linha 5)

    # TODO: Verificar corretude das mudanças feitas.
    # 1. normalizer
    # 2. obtenção das probabilidades
    # 3. calculo dos atributos

    GRAY_LEVELS = len(glcm)
   
    # Soma colunas e em seguida as linhas da matriz
    normalizer = np.add.reduce(np.add.reduce(glcm))

    # Normaliza
    probs = np.divide(glcm, normalizer) 
    probs_temp = np.copy(probs)
    # Fiz cópia acima para eliminar valores
    # fora do intervalo (0.0001,0.999)
    np.place(probs_temp, probs_temp < 0.0001, 1)
    np.place(probs_temp, probs_temp > 0.999, 1)
    # No caso prob = 1, temos log_prob = 0
    # Fiz isso de acordo com o original do Avinash.
    log_probs = np.log2(probs_temp)
    
    # TODO: explicar calculo dos atributos

    entropy = np.add.reduce(
                np.add.reduce(
                    np.multiply(
                        -probs, 
                        log_probs
                        )
                    )
                )

    energy = np.add.reduce(
            np.add.reduce(
                np.power(
                    probs, 
                    2
                    )
                )
            )

    # Matriz onde cada célula é LINHA - COLUNA
    msubn = [[line - col for col in range(GRAY_LEVELS)] for line in
            range(GRAY_LEVELS)]

    contrast = np.add.reduce(
                np.add.reduce(
                    np.multiply(
                        np.power(msubn, 2), 
                        probs
                        ) 
                    )
                )
    homogeneity = np.add.reduce(
                    np.add.reduce(
                        np.divide(
                            probs, 
                            1 + np.abs(msubn)
                            )
                        )
                    )
   
    # de Haralick's TexturalFeatures
    # sum(sum(i*j*p(i,j) - ux*uy))/sx*sy, 
    #   onde p(i,j) = probs, 
    #   e ux, uy, sx e sy são as médias e desvios de px(i), py(j)
#
#    correlation = 0
#    probs_y = np.add.reduce(probs)
#    probs_x = np.add.reduce(probs, axis=1)
#    mean_y = np.add.reduce([j*probs_y[j] for j in range(GRAY_LEVELS)])
#    mean_x = np.add.reduce([i*probs_x[i] for i in range(GRAY_LEVELS)])
#    
#    std_y = np.sqrt(np.add.reduce(
#        [(j - mean_y)**2 * np.add.reduce([probs[i][j] 
#                for i in range(GRAY_LEVELS)])
#            for j in range(GRAY_LEVELS)]
#        ))
#    std_x = np.sqrt(np.add.reduce(
#        [(i - mean_x)**2 * np.add.reduce([probs[i][j]
#                for j in range(GRAY_LEVELS)])
#            for i in range(GRAY_LEVELS)]
#        ))
#    for i in range(GRAY_LEVELS):
#        for j in range(GRAY_LEVELS):
#            correlation += (i*j * probs[i][j] - \
#                np.mean(probs_x)*np.mean(probs_y)) / 
#                   (np.std(probs_x) * np.std(probs))
    
    px = probs.sum(0)
    py = probs.sum(1)

    ux = np.dot(px, 255)
    uy = np.dot(py, 255)
    vx = np.dot(px, 255**2) - ux**2
    vy = np.dot(py, 255**2) - uy**2

    sx = np.sqrt(vx)
    sy = np.sqrt(vy)
   
    i,j = np.mgrid[:256,:256]
    ij = i*j

    correlation = (1. / sx / sy) * (np.dot(ij.ravel(), probs.ravel()) - ux * uy)

#    for i in range(GRAY_LEVELS):
#        for i in range(GRAY_LEVELS):
#            correlation += ((i*j) * probs[i][j] - \
#                    (mean_x*mean_y))/(std_x * std_y)
    
    if abs(entropy) < 0.0000001:
        entropy = 0
    
    attrs = [entropy, energy, contrast, homogeneity, correlation]

    return attrs