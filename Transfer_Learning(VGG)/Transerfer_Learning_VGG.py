# coding=gbk
import tensorflow as tf
from tensorflow.python import keras
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.applications.vgg16 import VGG16

# ����һ���࣬��ΪǨ��ģ��
class TransferModel(object):

    def __init__(self):
    # ����ѵ���Ͳ���ͼƬ�ı仯��������׼���Լ�������ǿ
        #ʵ����ѵ��������Լ���generator
        self.train_generator = ImageDataGenerator(rescale=1.0 / 255.0)
        self.test_generator = ImageDataGenerator(rescale=1.0 / 255.0)

        # ָ��ѵ�����ݺͲ��Ե�Ŀ¼
        self.train_dir = "./data/train"
        self.test_dir = "./data/test"

        # ����ͼƬѵ������������
        self.image_size = (224,224)
        self.batch_size = 32

        # ����Ǩ��ѧϰ�Ļ���ģ��
        # ������ȫ���Ӳ㣨3����VGGģ�Ͳ��Ҽ����˲���
        self.base_model = VGG16(weights='imagenet',include_top=False)

    def get_local_data(self):
        """
        ��ȡ���ص�ͼƬ���ݼ����
        :return:ѵ�����ݺͲ������ݵ�����
        """
        # ʹ��flow_from_derectory��ȡ����
        train_gen = self.train_generator.flow_from_directory(self.train_dir,
                                                 target_size=self.image_size, # VGGҪ���С��224��224��3��
                                                 batch_size=self.batch_size,
                                                 class_mode='binary',
                                                 shuffle=True) # �������ȡ
        test_gen = self.test_generator.flow_from_directory(self.test_dir,
                                                           target_size=self.image_size,
                                                           batch_size=self.batch_size,
                                                           class_mode='binary',
                                                           shuffle=True)
        return train_gen, test_gen

    def refine_base_model(self):
        """
        ΢��VGG�ṹ��5��blocks(5�з���)+ȫ��ƽ���ػ�+����ȫ���Ӳ�
        :return:
        """
        # ��ȡnotopģ�����
        # [?, ?, ?, 512]
        x = self.base_model.outputs[0]
        # ��ԭ������������ǵ�ģ�ͽṹ
        # [?, ?, ?, 512]��������>[?, 1 * 512]
        x = keras.layers.GlobalAveragePooling2D()(x)
        # �����µ�Ǩ��ģ��
        x = keras.layers.Dense(1024, activation=tf.nn.relu)(x) # 1024��Ԫ����ȫ���Ӳ�
        y_predict = keras.layers.Dense(5, activation=tf.nn.softmax)(x) # ȫ���Ӳ����ģ��

        # model������ģ��
        # ���룺VGGģ������(���������е�ģ�ͣ�Ϊ���ʼ������)�� ���Ϊ:y_predict
        transfer_model = keras.models.Model(inputs=self.base_model.inputs, outputs=y_predict)

        return transfer_model

if __name__ == '__main__':
    tm = TransferModel()
    train_gen, test_gen = tm.get_local_data()
    # print(train_gen)
    # for data in train_gen:
    #     print(data)
    # print(tm.base_model.summary())
    model = tm.refine_base_model()
    print(model)
