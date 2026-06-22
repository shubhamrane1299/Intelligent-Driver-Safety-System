from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(

    rescale=1./255,

    validation_split=0.2
)

train = datagen.flow_from_directory(

    "mask_dataset",

    target_size=(64,64),

    batch_size=32,

    class_mode="binary",

    subset="training"
)

val = datagen.flow_from_directory(

    "mask_dataset",

    target_size=(64,64),

    batch_size=32,

    class_mode="binary",

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

model.add(Flatten())

model.add(Dense(128,activation="relu"))

model.add(Dense(1,activation="sigmoid"))

model.compile(

    optimizer="adam",

    loss="binary_crossentropy",

    metrics=["accuracy"]
)

model.fit(

    train,

    validation_data=val,

    epochs=5
)

model.save("models/mask_model.h5")

print("MASK MODEL TRAINED")