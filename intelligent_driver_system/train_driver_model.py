from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator

IMG_SIZE = 64

datagen = ImageDataGenerator(

    rescale=1./255,

    validation_split=0.2,

    rotation_range=10,

    zoom_range=0.2,

    brightness_range=[0.5,1.5],

    horizontal_flip=True
)

train = datagen.flow_from_directory(

    "dataset/train",

    target_size=(64,64),

    batch_size=32,

    class_mode="categorical",

    subset="training"
)

val = datagen.flow_from_directory(

    "dataset/train",

    target_size=(64,64),

    batch_size=32,

    class_mode="categorical",

    subset="validation"
)

model = Sequential()

model.add(

    Conv2D(

        32,

        (3,3),

        activation="relu",

        input_shape=(64,64,3)
    )
)

model.add(MaxPooling2D(2,2))

model.add(

    Conv2D(

        64,

        (3,3),

        activation="relu"
    )
)

model.add(MaxPooling2D(2,2))

model.add(

    Conv2D(

        128,

        (3,3),

        activation="relu"
    )
)

model.add(MaxPooling2D(2,2))

model.add(Flatten())

model.add(Dense(256,activation="relu"))

model.add(Dropout(0.5))

model.add(Dense(4,activation="softmax"))

model.compile(

    optimizer="adam",

    loss="categorical_crossentropy",

    metrics=["accuracy"]
)

model.fit(

    train,

    validation_data=val,

    epochs=10
)

model.save("models/driver_model.h5")

print("DRIVER MODEL TRAINED")