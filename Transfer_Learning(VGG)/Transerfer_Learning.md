# Machine Vision based CNN
�����Ӿ�����CNN����������
## Ǩ��ѧϰ
**Ǩ��ѧϰ��** �������ݡ������ģ�ͼ����ʶ�ԣ����ɵ�����ѧϰ����ѵ���õ�ģ�ͣ�Ӧ�����µ�����������һ�����̡�
> ע�⣺�������������������ͬһ���ʣ�����ͼ����߶����������߶���������ġ�

`ԭģ��(���нϺõĻ�������)--->�޸�ԭģ�͵�������--->�õ��µ�ģ��(�������µ�����)`

- �ھ��к���������Դ��ʱ�򣬾Ϳ��Բ�ʹ��Ǩ��ѧϰ������ֱ��ʹ�����ѧϰѵ����һ��³���Ժõ�ģ��
- Ǩ��ѧϰ���Խ���ѵ���ɱ���վ�ھ��˵ļ���ϣ���ͷѵ����Ҫ�ϳ�ʱ������Ҫ�����ϴ��GPU��Դ��

### ΢����fine-tuning��
**΢����**
- ����ģ�Ͳ���������Ҫ��������
- ����ģ�ͽṹ������Ҫ��������

**Ԥѵ��ģ��(pre-trained model):** ������������Ǩ��ѧϰ������ģ�͡�
https://github.com/tensorflow/models/tree/master/research/slim

### Ǩ��ѧϰ����
![img.png](picture/img1.png)
1. �����Լ������磬��Ԥѵ��ģ�ͻ����ϣ��޸��������ṹ����������ѵ��ģ�͵�ģ�Ͳ���
2. �������ݴ�С����
   - �����ѵ��ģ��������С����ô���ǿ���ѡ��Ԥѵ��ģ�͵����еĲ����freeze(����ͨ��Tensorflow��trainable=False����ʵ��)����ʣ�µ�����㲿�ֿ���ѡ���������ѵ����
   - �����ѵ��ģ������������ô���ǿ��Խ�Ԥѵ��ģ����һ����ߴ󲿷ֵĲ����freeze����ʣ�µĲ��ֵ�layer���Խ������������ݻ�����΢����

# VGG
����Ŀ��������VGGģ��
1. ׼��ѵ��������Լ�
2. �޸�ģ�ͷ����
3. freezeԭʼVGGģ��
4. ѵ��ģ��
5. �������ݽ���Ԥ��

## ׼��ѵ��������Լ�
### ���api
- ImageDataGenerator()
   - �������ݵ�ת������������ǿ
   - ����ͼƬ����������ֵ���ṩ������ǿ����
   - rescale=1.0 / 255,:��׼��
   - zca_whitening=False: # zca�׻������������ͼƬ����PCA��ά����������ͼƬ��������Ϣ
   - rotation_range=20:Ĭ��0�� ��ת�Ƕȣ�������Ƕȷ�Χ�������һ��ֵ
   - width_shift_range=0.2,:Ĭ��0��ˮƽƽ��
   - height_shift_range=0.2:Ĭ��0�� ��ֱƽ��
   - shear_range=0.2:# ƽ�Ʊ任
   - zoom_range=0.2:
   - horizontal_flip=True:ˮƽ��ת


- train_generator = ImageDataGenerator()
  - flow(x, y, batch_size)
    - ֱ�Ӵ��ļ���ȡ
  - flow_from_directory(
    - directory=path,# ��ȡĿ¼ 
    - target_size=(h,w),# Ŀ����״ 
    - batch_size=size,# ��������С 
    - class_mode='binary', # Ŀ��ֵ��ʽ 
    - shuffle=True)
      - �ӱ��ض�ȡ
      - ��apiҪ�����ݴ洢��ʽ�̶�
```
data/
    train/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
    validation/
        dogs/
            dog001.jpg
            dog002.jpg
            ...
        cats/
            cat001.jpg
            cat002.jpg
            ...
```

> ע�������ڽ���������ǿ����ѵ����ʱ��ҲҪ����ǿ���ݷŽ�ȥ����ʹ��fit_generator()��������fit()

## �޸�ģ�ͷ����
### VGG-notopģ��
������������
�ڸ�Ŀ¼����һ��```.keras```�����е�```models```�ļ����о�����һ��VGG��notopģ��
![img.png](picture/img.png)
- notopģ�Ͳ������������ȫ���Ӳ㣬ר������fine-tuning������Ҫ��������������ɾ��

VGG16Դ��Ƭ
```java
 if include_top:
    # Classification block
    x = layers.Flatten(name='flatten')(x)
    x = layers.Dense(4096, activation='relu', name='fc1')(x)
    x = layers.Dense(4096, activation='relu', name='fc2')(x)

    imagenet_utils.validate_activation(classifier_activation, weights)
    x = layers.Dense(classes, activation=classifier_activation,
                     name='predictions')(x)
  else:
    if pooling == 'avg':
      x = layers.GlobalAveragePooling2D()(x)
    elif pooling == 'max':
      x = layers.GlobalMaxPooling2D()(x)

 # Ensure that the model takes into account
  # any potential predecessors of `input_tensor`.
  if input_tensor is not None:
    inputs = layer_utils.get_source_inputs(input_tensor)
  else:
    inputs = img_input
  # Create model.
  model = training.Model(inputs, x, name='vgg16')
  
  # Load weights.
  if weights == 'imagenet':
    if include_top:
      weights_path = data_utils.get_file(
          'vgg16_weights_tf_dim_ordering_tf_kernels.h5',
          WEIGHTS_PATH,
          cache_subdir='models',
          file_hash='64373286793e3c8b2b4e3219cbf3544b')
    else:
      weights_path = data_utils.get_file(
          'vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5',
          WEIGHTS_PATH_NO_TOP,
          cache_subdir='models',
          file_hash='6d6bbae143d832006294945121d1f1fc')
    model.load_weights(weights_path)
  elif weights is not None:
    model.load_weights(weights)

  return model
```
������VGG16��imgenet��ģ�ͱ���
![img.png](picture/img2.png)
### ȫ��ƽ���ػ�(GobalAveragePooling2D)
�ڽ���Ǩ��ѧϰ�У�����Ҫȥѵ�������ȫ���Ӳ㣬���Բ���Ҫ�����Ĳ�����ʹ�ù�������ᵼ�¹���ϡ�
���磺�������Ϊshape=[8,8,2048],ͨ��ȫ��ƽ���ػ��󣬽�8*8��64λ��������ȡ��ֵ������ԭ����8*8*2048��ת�����1*2048
![](picture/pooling.png)

## ����Ԥѵ��ģ��
�������ģ�͵Ĳ��Լ��󣬾Ϳ��Խ�ģ�͵����в����ó���һ��ѵ����
�������ģ�͵Ĳ��Լ�С���ͽ�ģ��ǰ��㶳�ᣬֻѵ��ȫ���Ӳ�Ĳ���

�ڽ��ж���ģ��֮ǰ��������Ҫ֪������API��
- ����ģ��
```java
model.save_weights("./xxx.h5")
```
- ����ģ��
```java
model.load_weights("./xxx.h5")
```




