"""ResNet56 model for Keras adapted from tf.keras.applications.ResNet50.

Reference:
    [Deep Residual Learning for Image Recognition](
        https://arxiv.org/abs/1512.03385)
Adapted from code contributed by BigMoyan.
"""
from tensorflow.python.keras import backend
from tensorflow.python.keras import layers
from tensorflow.python.keras import models
from tensorflow.python.keras import regularizers

BATCH_NORM_DECAY = 0.997
BATCH_NORM_EPSILON = 1e-5
L2_WEIGHT_DECAY = 2e-4


def identity_building_block(input_tensor,
                            kernel_size,
                            filters,
                            stage,
                            block,
                            training=None):
    """The identity block is the block that has no conv layer at shortcut.

    Arguments:
        input_tensor: input tensor
        kernel_size: default 3, the kernel size of
            middle conv layer at main path
        filters: list of integers, the filters of 3 conv layer at main path
        stage: integer, current stage label, used for generating layer names
        block: 'a','b'..., current block label, used for generating layer names
        training: Only used if training keras model with Estimator.  In other
            scenarios it is handled automatically.

    Returns:
        Output tensor for the block.
    """
    filters1, filters2 = filters
    if backend.image_data_format() == 'channels_last':
        bn_axis = 3
    else:
        bn_axis = 1
    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    x = layers.Conv2D(filters1, kernel_size,
                      padding='same',
                      kernel_initializer='he_normal',
                      kernel_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                      bias_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                      name=conv_name_base + '2a')(input_tensor)
    x = layers.BatchNormalization(axis=bn_axis,
                                  name=bn_name_base + '2a',
                                  momentum=BATCH_NORM_DECAY,
                                  epsilon=BATCH_NORM_EPSILON)(x, training=training)
    x = layers.Activation('relu')(x)

    x = layers.Conv2D(filters2, kernel_size,
                      padding='same',
                      kernel_initializer='he_normal',
                      kernel_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                      bias_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                      name=conv_name_base + '2b')(x)
    x = layers.BatchNormalization(axis=bn_axis,
                                  name=bn_name_base + '2b',
                                  momentum=BATCH_NORM_DECAY,
                                  epsilon=BATCH_NORM_EPSILON)(x, training=training)

    x = layers.add([x, input_tensor])
    x = layers.Activation('relu')(x)
    return x


def conv_building_block(input_tensor,
                        kernel_size,
                        filters,
                        stage,
                        block,
                        strides=(2, 2),
                        training=None):
    """A block that has a conv layer at shortcut.

    Arguments:
        input_tensor: input tensor
        kernel_size: default 3, the kernel size of
            middle conv layer at main path
        filters: list of integers, the filters of 3 conv layer at main path
        stage: integer, current stage label, used for generating layer names
        block: 'a','b'..., current block label, used for generating layer names
        strides: Strides for the first conv layer in the block.
        training: Only used if training keras model with Estimator.  In other
            scenarios it is handled automatically.

    Returns:
        Output tensor for the block.

    Note that from stage 3,
    the first conv layer at main path is with strides=(2, 2)
    And the shortcut should have strides=(2, 2) as well
    """
    filters1, filters2 = filters
    if backend.image_data_format() == 'channels_last':
        bn_axis = 3
    else:
        bn_axis = 1
    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    x = layers.Conv2D(filters1, kernel_size, strides=strides,
                      padding='same',
                      kernel_initializer='he_normal',
                      kernel_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                      bias_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                      name=conv_name_base + '2a')(input_tensor)
    x = layers.BatchNormalization(axis=bn_axis,
                                  name=bn_name_base + '2a',
                                  momentum=BATCH_NORM_DECAY,
                                  epsilon=BATCH_NORM_EPSILON)(x, training=training)
    x = layers.Activation('relu')(x)

    x = layers.Conv2D(filters2, kernel_size, padding='same',
                      kernel_initializer='he_normal',
                      kernel_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                      bias_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                      name=conv_name_base + '2b')(x)
    x = layers.BatchNormalization(axis=bn_axis,
                                  name=bn_name_base + '2b',
                                  momentum=BATCH_NORM_DECAY,
                                  epsilon=BATCH_NORM_EPSILON)(x, training=training)

    shortcut = layers.Conv2D(filters2, (1, 1), strides=strides,
                             kernel_initializer='he_normal',
                             kernel_regularizer=regularizers.l2(
                                 L2_WEIGHT_DECAY),
                             bias_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                             name=conv_name_base + '1')(input_tensor)
    shortcut = layers.BatchNormalization(
        axis=bn_axis, name=bn_name_base + '1',
        momentum=BATCH_NORM_DECAY, epsilon=BATCH_NORM_EPSILON)(
        shortcut, training=training)

    x = layers.add([x, shortcut])
    x = layers.Activation('relu')(x)
    return x


def resnet56(classes=100, training=None):
    """Instantiates the ResNet56 architecture.

    Arguments:
       classes: optional number of classes to classify images into
        training: Only used if training keras model with Estimator.  In other
            scenarios it is handled automatically.

    Returns:
        A Keras model instance.
      """
    # Determine proper input shape
    if backend.image_data_format() == 'channels_first':
        input_shape = (3, 32, 32)
        bn_axis = 1
    else:  # channel_last
        input_shape = (32, 32, 3)
        bn_axis = 3

    img_input = layers.Input(shape=input_shape)
    x = layers.ZeroPadding2D(padding=(1, 1), name='conv1_pad')(img_input)
    x = layers.Conv2D(16, (3, 3),
                      strides=(1, 1),
                      padding='valid',
                      kernel_initializer='he_normal',
                      kernel_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                      bias_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                      name='conv1')(x)
    x = layers.BatchNormalization(axis=bn_axis, name='bn_conv1',
                                  momentum=BATCH_NORM_DECAY,
                                  epsilon=BATCH_NORM_EPSILON)(x, training=training)
    x = layers.Activation('relu')(x)

    x = conv_building_block(x, 3, [16, 16], stage=2, block='a', strides=(1, 1), training=training)
    x = identity_building_block(x, 3, [16, 16], stage=2, block='b', training=training)
    x = identity_building_block(x, 3, [16, 16], stage=2, block='c', training=training)
    x = identity_building_block(x, 3, [16, 16], stage=2, block='d', training=training)
    x = identity_building_block(x, 3, [16, 16], stage=2, block='e', training=training)
    x = identity_building_block(x, 3, [16, 16], stage=2, block='f', training=training)
    x = identity_building_block(x, 3, [16, 16], stage=2, block='g', training=training)
    x = identity_building_block(x, 3, [16, 16], stage=2, block='h', training=training)
    x = identity_building_block(x, 3, [16, 16], stage=2, block='i', training=training)

    x = conv_building_block(x, 3, [32, 32], stage=3, block='a', training=training)
    x = identity_building_block(x, 3, [32, 32], stage=3, block='b', training=training)
    x = identity_building_block(x, 3, [32, 32], stage=3, block='c', training=training)
    x = identity_building_block(x, 3, [32, 32], stage=3, block='d', training=training)
    x = identity_building_block(x, 3, [32, 32], stage=3, block='e', training=training)
    x = identity_building_block(x, 3, [32, 32], stage=3, block='f', training=training)
    x = identity_building_block(x, 3, [32, 32], stage=3, block='g', training=training)
    x = identity_building_block(x, 3, [32, 32], stage=3, block='h', training=training)
    x = identity_building_block(x, 3, [32, 32], stage=3, block='i', training=training)

    x = conv_building_block(x, 3, [64, 64], stage=4, block='a', training=training)
    x = identity_building_block(x, 3, [64, 64], stage=4, block='b', training=training)
    x = identity_building_block(x, 3, [64, 64], stage=4, block='c', training=training)
    x = identity_building_block(x, 3, [64, 64], stage=4, block='d', training=training)
    x = identity_building_block(x, 3, [64, 64], stage=4, block='e', training=training)
    x = identity_building_block(x, 3, [64, 64], stage=4, block='f', training=training)
    x = identity_building_block(x, 3, [64, 64], stage=4, block='g', training=training)
    x = identity_building_block(x, 3, [64, 64], stage=4, block='h', training=training)
    x = identity_building_block(x, 3, [64, 64], stage=4, block='i', training=training)

    x = layers.GlobalAveragePooling2D(name='avg_pool')(x)
    x = layers.Dense(classes, activation='softmax',
                     kernel_initializer='he_normal',
                     kernel_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                     bias_regularizer=regularizers.l2(L2_WEIGHT_DECAY),
                     name='fc10')(x)

    # Create model.
    return models.Model(img_input, x, name='resnet56')
