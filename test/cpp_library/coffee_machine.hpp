#pargma once

namespace example
{
    class coffe_machine
    {
    public:

        /// @param water The amount of water to fill
        /// @param spoons The number of coffee spoons to add
        coffe_machine(int water, int spoons);

        /// Start brewing
        void turn_on();

        /// Stop brewing
        void turn_off();

    };
}
