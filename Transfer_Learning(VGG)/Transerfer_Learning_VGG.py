# coding=gbk
import numpy as np
import tensorflow as tf
from tensorflow.python import keras
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tensorflow.python.keras.applications.vgg16 import VGG16, preprocess_input

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

        self.label_dict = {
            '0': 'bus',
            '1': 'dinosaurs',
            '2': 'elephants',
            '3': 'flowers',
            '4': 'horse'
        }

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

    def freeze_model(self):
        """
        �������ģ�ͣ�5 blocks��
        ����������ѵ�����Ĵ�С����
        :return:
        """
        # ��ȡ���в㣬���ز���б�
        for layer in self.base_model.layers:
            layer.trainable = False

    def compile(self, model):
        """
        ����ģ��
        :return:
        """
        model.compile(optimizer=tf.keras.optimizers.Adam(),
                                loss=keras.losses.sparse_categorical_crossentropy,
                                metrics=['accuracy'])
        return None

    def fit_generator(self, model, train_gen, test_gen):
        """
        ѵ��ģ�ͣ�������ǿ������Ҫʹ��fit_generator()
        ���ǣ��ص����ˣ����°汾��tensorflow��fit_generator()�Ѿ��������ˣ�fit()�ϲ���fit_generator()������
        :return:
        """
        # ��h5�ļ���¼ÿһ�ε����е�׼ȷ��
        modelckpt = keras.callbacks.ModelCheckpoint('./ckpt/transfer_{epoch:02d}-{val_accuracy:.2f}.h5',
                                        montitor='val_acc',
                                        save_weights_only=True,
                                        save_best_only=True,
                                        mode='auto',
                                        period=1)
        # ��˵һ�飺���°汾��tensorflow��fit_generator()�Ѿ��������ˣ�fit()�ϲ���fit_generator()������
        model.fit(train_gen, epochs=3, validation_data=test_gen, callbacks=[modelckpt])
        return None

    def predict(self,model):
        """
        Ԥ�����
        :return:
        """

        # ����ģ�ͣ�����ѵ��ȫ���Ӳ��ģ�ͣ�transfer_model��
        model.load_weights("./ckpt/transfer_03-0.93.h5")
        # ��ȡ��ʶ��ͼƬ
        image = load_img("./data/test/a.jpg", target_size=(224,224))
        image = img_to_array(image)
        # �����������Ҫ��ά���ݣ�ת��Ϊ��ά
        # (x,y,z)����>(1,x,y,z)
        # ע�����ﲻ��ʹ��tf.reshape����Ϊ�������õ���image����һ��tensor���󣬾Ͳ��ܽ��к�������Ĳ�����
        img = image.reshape([1, image.shape[0], image.shape[1], image.shape[2]])
        # Ԥ��

        # Ԥ��������
        image = preprocess_input(img)
        predictons = model.predict(image)
        res = np.argmax(predictons, axis=1)
        print(self.label_dict[str(res[0])])

if __name__ == '__main__':
    tm = TransferModel()
    """ 
    #ѵ��ģ��
    train_gen, test_gen = tm.get_local_data()
    # print(train_gen)
    # for data in train_gen:
    #     print(data)
    # print(tm.base_model.summary())
    model = tm.refine_base_model()
    # print(model)
    tm.freeze_model()
    tm.compile(model)
    tm.fit_generator(model,train_gen,test_gen)
    """

    #����ģ��
    model = tm.refine_base_model()
    tm.predict(model)

